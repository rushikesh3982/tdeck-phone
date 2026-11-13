/*
 * T-Deck phone: test program for the assembled phone.
 *
 * - Turns on the T-Deck's peripheral power (GPIO10). That also powers the Grove 3.3 V, which feeds the modem
 *   board's VDD (the reference for its level shifters).
 * - Talks to the KTRON A7672S modem on the Grove pins: GPIO43 sends, GPIO44 receives, 115200 baud. The wires go
 *   straight across (TX to TX, RX to RX), as tested on the bench.
 * - Shows the modem's state on the screen, refreshed every few seconds: modem, SIM, network, VoLTE, 4G signal (with
 *   a 5-reading average, for the antenna test), battery, GPS, calls and SMS.
 * - Beeps twice on the T-Deck's speaker at start, and on every ring: the speaker's test, and a ringtone.
 * - Passes a serial terminal on the Mac (USB-C, 115200 baud) straight through to the modem, so every AT command in
 *   docs/bring-up.md works. After anything is typed, the screen stops asking the modem for 20 s, so the replies on
 *   the Mac aren't mixed with its own.
 *
 * Privacy: the screen never shows a phone number, the IMEI, the SIM's number or a GPS position, so it can be
 * photographed for the build log. The terminal on the Mac shows everything the modem says.
 *
 * Pins and the display's start-up are from LilyGO's own T-Deck examples (github.com/Xinyuan-LilyGO/T-Deck).
 * MIT licence, like the rest of this repository.
 */
#include <Arduino.h>
#include <SPI.h>
#include <TFT_eSPI.h>
#include <driver/i2s.h>

// ---- T-Deck pins (LilyGO, examples/HelloWorld/utilities.h)
constexpr int PIN_POWER_ON = 10;
constexpr int PIN_TFT_CS = 12;
constexpr int PIN_SD_CS = 39;
constexpr int PIN_RADIO_CS = 9;
constexpr int PIN_SPI_SCK = 40;
constexpr int PIN_SPI_MISO = 38;
constexpr int PIN_SPI_MOSI = 41;
constexpr int PIN_BACKLIGHT = 42;
constexpr int PIN_BATTERY = 4;        // the battery, through a 1:2 divider
constexpr int PIN_MODEM_RX = 44;      // Grove RX: what the modem says
constexpr int PIN_MODEM_TX = 43;      // Grove TX: commands to the modem
constexpr int PIN_SPK_BCK = 7;        // the speaker's amplifier (MAX98357A), I2S
constexpr int PIN_SPK_WS = 5;
constexpr int PIN_SPK_DOUT = 6;

constexpr uint32_t BAUD = 115200;
constexpr float BATTERY_DIVIDER = 2.0f;
constexpr uint32_t POLL_EVERY_MS = 700;          // one status question to the modem this often
constexpr uint32_t TERMINAL_PAUSE_MS = 20000;    // no status questions for this long after the Mac sends anything
constexpr uint32_t GPS_RETRY_MS = 90000;         // GPS off and on again if it hasn't said READY by then
constexpr int MODEM_LOST_AFTER = 3;              // unanswered ATs before the modem counts as off

HardwareSerial &modem = Serial1;
TFT_eSPI tft;

// ---- the display's start-up for the T-Deck's panel (LilyGO, examples/HelloWorld: "used when the display is
// abnormal after the TFT_eSPI update"). len | 0x80: wait 120 ms after the command.
struct LcdCmd {
    uint8_t cmd;
    uint8_t data[14];
    uint8_t len;
};
static const LcdCmd LCD_INIT[] = {
    {0x01, {0}, 0 | 0x80},
    {0x11, {0}, 0 | 0x80},
    {0x3A, {0X05}, 1},
    {0x36, {0x55}, 1},
    {0xB2, {0x0C, 0x0C, 0X00, 0X33, 0X33}, 5},
    {0xB7, {0X75}, 1},
    {0xBB, {0X1A}, 1},
    {0xC0, {0X2C}, 1},
    {0xC2, {0X01}, 1},
    {0xC3, {0X13}, 1},
    {0xC4, {0X20}, 1},
    {0xC6, {0X0F}, 1},
    {0xD0, {0XA4, 0XA1}, 2},
    {0xD6, {0XA1}, 1},
    {0xE0, {0XD0, 0X0D, 0X14, 0X0D, 0X0D, 0X09, 0X38, 0X44, 0X4E, 0X3A, 0X17, 0X18, 0X2F, 0X30}, 14},
    {0xE1, {0XD0, 0X09, 0X0F, 0X08, 0X07, 0X14, 0X37, 0X44, 0X4D, 0X38, 0X15, 0X16, 0X2C, 0X3E}, 14},
    {0x21, {0}, 0},
    {0x29, {0}, 0},
    {0x2C, {0}, 0},
};

// ---- the screen: one row per item
enum Row { R_MODEM, R_SIM, R_NETWORK, R_VOLTE, R_SIGNAL, R_AVERAGE, R_BATTERY, R_GPS, R_CALL, R_SMS, R_MAC, ROWS };
static const char *LABELS[ROWS] = {"Modem", "SIM",  "Network", "VoLTE", "4G signal", "Average",
                                   "Battery", "GPS", "Call",    "SMS",   "Mac"};
constexpr int TOP = 26, ROW_H = 17, VALUE_X = 84;   // values fit about 27 characters
constexpr uint16_t C_OK = TFT_GREEN, C_WAIT = TFT_YELLOW, C_BAD = TFT_RED, C_INFO = TFT_WHITE, C_DIM = TFT_DARKGREY;

String rowText[ROWS], shownText[ROWS];
uint16_t rowColor[ROWS], shownColor[ROWS];

void setRow(Row r, const String &text, uint16_t color)
{
    rowText[r] = text;
    rowColor[r] = color;
}

void drawFrame()
{
    tft.fillScreen(TFT_BLACK);
    tft.fillRect(0, 0, 320, 21, TFT_NAVY);
    tft.setTextColor(TFT_WHITE, TFT_NAVY);
    tft.setTextPadding(0);
    tft.drawString("T-Deck phone: test program", 6, 3, 2);
    tft.setTextColor(C_DIM, TFT_BLACK);
    for (int r = 0; r < ROWS; r++) {
        tft.drawString(LABELS[r], 4, TOP + r * ROW_H, 2);
    }
    tft.drawString("Mac: USB-C serial, 115200 baud. Type AT commands;", 4, 218, 1);
    tft.drawString("this screen pauses its questions for 20 s after.", 4, 228, 1);
    for (int r = 0; r < ROWS; r++) {
        shownText[r] = "\x01";          // forces a first draw
    }
}

void drawRows()
{
    for (int r = 0; r < ROWS; r++) {
        if (rowText[r] == shownText[r] && rowColor[r] == shownColor[r]) {
            continue;
        }
        tft.setTextColor(rowColor[r], TFT_BLACK);
        tft.setTextPadding(320 - VALUE_X);
        tft.drawString(rowText[r], VALUE_X, TOP + r * ROW_H, 2);
        shownText[r] = rowText[r];
        shownColor[r] = rowColor[r];
    }
}

// ---- what the program knows about the modem
bool modemAlive = false;
bool needSetup = true;
int missedAts = 0;
String modelName;
String operatorName;
bool lteNow = false;
bool gpsReady = false;
uint32_t gpsStartedAt = 0;
uint32_t callShownAt = 0;
bool ringPending = false;
float modemVolts = -1;

int rsrpHistory[5];
int rsrpCount = 0;
int rsrpBand = -1;

// ---- talking to the modem
String partial;             // modem bytes since the last line end
uint32_t lastTyped = 0;     // the last time the Mac sent anything
bool typedEver = false;

bool terminalBusy()
{
    return typedEver && millis() - lastTyped < TERMINAL_PAUSE_MS;
}

// Lines the modem sends by itself, not as a reply to a question.
bool isEvent(const String &line)
{
    static const char *starts[] = {"RING",      "+CLIP:",   "VOICE CALL:", "NO CARRIER", "MISSED_CALL", "+CMTI:",
                                   "+CGNSSPWR:", "*ATREADY", "SMS DONE",    "PB DONE",    "+CGEV:"};
    for (auto s : starts) {
        if (line.startsWith(s)) {
            return true;
        }
    }
    return false;
}

void handleEvent(const String &line)
{
    if (line == "RING") {
        setRow(R_CALL, "ringing (ATA answers)", C_WAIT);
        callShownAt = millis();
        ringPending = true;                   // beeps once the line has been handled
    } else if (line.startsWith("VOICE CALL: BEGIN")) {
        setRow(R_CALL, lteNow ? "in a call, on 4G (VoLTE)" : "in a call", C_OK);
        callShownAt = 0;
    } else if (line.startsWith("VOICE CALL: END") || line == "NO CARRIER") {
        setRow(R_CALL, "call ended", C_INFO);
        callShownAt = millis();
    } else if (line.startsWith("MISSED_CALL")) {
        setRow(R_CALL, "missed call", C_INFO);
        callShownAt = millis();
    } else if (line.startsWith("+CMTI:")) {
        String index = line.substring(line.lastIndexOf(',') + 1);
        index.trim();
        setRow(R_SMS, "new: AT+CMGR=" + index + " reads it", C_OK);
    } else if (line.startsWith("+CGNSSPWR: READY")) {
        gpsReady = true;
    } else if (line.startsWith("*ATREADY")) {
        needSetup = true;             // the modem has just started
    }
}

// A whole line from the modem. forward: also show it on the Mac (when the terminal isn't already getting raw bytes).
void onLine(const String &line, bool forward)
{
    if (forward) {
        Serial.print(line);
        Serial.print("\r\n");
    }
    handleEvent(line);
}

// Anything typed on the Mac goes straight to the modem.
void pumpUsb()
{
    while (Serial.available()) {
        modem.write(Serial.read());
        lastTyped = millis();
        typedEver = true;
    }
}

// The modem's output. While the Mac's terminal is in use it gets every byte (the SMS prompt "> " has no line end);
// otherwise only the modem's own events are shown there.
void pumpModem()
{
    bool raw = terminalBusy();
    while (modem.available()) {
        char c = modem.read();
        if (raw) {
            Serial.write(c);
        }
        if (c == '\n') {
            partial.trim();
            if (partial.length()) {
                onLine(partial, !raw && isEvent(partial));
            }
            partial = "";
        } else if (c != '\r' && partial.length() < 400) {
            partial += c;
        }
    }
}

// One question from the status screen. Its reply lines (without the echo and the final OK) go into reply.
// Returns true on OK. Events that arrive meanwhile (a call, an SMS) are handled as usual.
bool command(const char *cmd, String &reply, uint32_t timeoutMs = 1500)
{
    reply = "";
    pumpModem();
    modem.print(cmd);
    modem.print("\r");
    String line;
    uint32_t t0 = millis();
    while (millis() - t0 < timeoutMs) {
        while (modem.available()) {
            char c = modem.read();
            if (c != '\n') {
                if (c != '\r' && line.length() < 400) {
                    line += c;
                }
                continue;
            }
            line.trim();
            if (line == "OK") {
                return true;
            } else if (line == "ERROR" || line.startsWith("+CME ERROR") || line.startsWith("+CMS ERROR")) {
                reply = line;
                return false;
            } else if (line.length() && line != cmd) {      // not the modem's echo of the command
                if (isEvent(line)) {
                    onLine(line, true);
                } else {
                    reply += line;
                    reply += '\n';
                }
            }
            line = "";
        }
        delay(2);
    }
    return false;
}

// ---- reading the replies
String lineStarting(const String &reply, const char *prefix)
{
    int at = reply.indexOf(prefix);
    if (at < 0) {
        return "";
    }
    int end = reply.indexOf('\n', at);
    return reply.substring(at, end < 0 ? reply.length() : end);
}

// The fields after a reply's colon, split at commas.
int fields(const String &line, String *out, int maxFields)
{
    int colon = line.indexOf(':');
    String rest = colon >= 0 ? line.substring(colon + 1) : line;
    rest.trim();
    int n = 0, start = 0;
    for (int i = 0; i <= (int)rest.length() && n < maxFields; i++) {
        if (i == (int)rest.length() || rest[i] == ',') {
            out[n] = rest.substring(start, i);
            out[n].trim();
            n++;
            start = i + 1;
        }
    }
    return n;
}

String firstLine(const String &s)
{
    String t = s;
    t.trim();
    int nl = t.indexOf('\n');
    return nl >= 0 ? t.substring(0, nl) : t;
}

String quoted(const String &line)
{
    int a = line.indexOf('"');
    int b = line.indexOf('"', a + 1);
    return (a >= 0 && b > a) ? line.substring(a + 1, b) : "";
}

// CPSI's RSRP: this board's firmware gave 0..97 (dBm + 140) on the bench; other firmware gives dBm, or tenths of one.
int rsrpDbm(int v)
{
    if (v >= 0 && v <= 97) {
        return v - 140;
    }
    if (v < -200) {
        return v / 10;
    }
    return v;
}

const char *rsrpWord(int dbm)
{
    return dbm >= -80 ? "excellent" : dbm >= -90 ? "good" : dbm >= -100 ? "fair" : dbm >= -110 ? "weak" : "very weak";
}

void addRsrp(int band, int dbm)
{
    if (band != rsrpBand) {
        rsrpBand = band;
        rsrpCount = 0;
    }
    if (rsrpCount == 5) {
        memmove(rsrpHistory, rsrpHistory + 1, 4 * sizeof(int));
        rsrpCount = 4;
    }
    rsrpHistory[rsrpCount++] = dbm;
    float sum = 0;
    for (int i = 0; i < rsrpCount; i++) {
        sum += rsrpHistory[i];
    }
    char buf[60];
    if (rsrpCount < 5) {
        snprintf(buf, sizeof buf, "%.1f dBm (%d of 5 so far)", sum / rsrpCount, rsrpCount);
    } else {
        snprintf(buf, sizeof buf, "%.1f dBm, last 5, B%d", sum / 5, band);
    }
    setRow(R_AVERAGE, buf, rsrpCount < 5 ? C_WAIT : C_INFO);
}

// ---- the status questions, one at a time
void modemLost()
{
    modemAlive = false;
    needSetup = true;
    lteNow = false;
    gpsReady = false;
    modemVolts = -1;
    rsrpCount = 0;
    rsrpBand = -1;
    setRow(R_MODEM, "no answer: switch on?", C_BAD);
    for (int r = R_SIM; r <= R_GPS; r++) {
        if (r != R_BATTERY) {
            setRow((Row)r, "-", C_DIM);
        }
    }
}

void setUpModem()
{
    String reply;
    // ATE1: the modem repeats what's typed, so the Mac's terminal shows it. The rest: caller number with RING, SMS
    // as text and announced when they arrive, call sound to the earpiece, GPS on.
    // Earpiece volume 5 and mic gain 4 are the levels found right on the bench.
    static const char *setup[] = {"ATE1", "AT+CLIP=1", "AT+CMGF=1", "AT+CNMI=2,1,0,0,0", "AT+CSDVC=1",
                                  "AT+COUTGAIN=5", "AT+CMICGAIN=4", "AT+CGNSSPWR=1"};
    for (auto cmd : setup) {
        command(cmd, reply);
    }
    gpsStartedAt = millis();
    if (command("AT+CGMM", reply)) {
        modelName = reply;
        modelName.trim();
    }
    needSetup = false;
}

void askModem()
{
    static int step = 0;
    String reply;

    if (!modemAlive || step == 0) {
        bool ok = command("AT", reply, modemAlive ? 1500 : 500);
        if (ok) {
            missedAts = 0;
            if (!modemAlive) {
                modemAlive = true;
                needSetup = true;
            }
            if (needSetup) {
                setRow(R_MODEM, "answering, setting up", C_WAIT);
                setUpModem();
            }
            String state = "answering";
            if (modelName.length()) {
                state += " (" + modelName + ")";
            }
            setRow(R_MODEM, state, C_OK);
        } else if (++missedAts >= MODEM_LOST_AFTER || !modemAlive) {
            modemLost();
            return;
        }
        step = 1;
        return;
    }

    String f[20];
    switch (step) {
    case 1: {   // SIM
        bool ok = command("AT+CPIN?", reply);
        String line = lineStarting(reply, "+CPIN:");
        if (ok && line.indexOf("READY") >= 0) {
            setRow(R_SIM, "ready", C_OK);
        } else if (line.indexOf("PIN") >= 0) {
            setRow(R_SIM, "asks for its PIN", C_BAD);
        } else if (reply.indexOf("not inserted") >= 0 || reply.indexOf("ERROR: 10") >= 0 ||
                   reply.indexOf("REMOVED") >= 0) {
            setRow(R_SIM, "not found: reinsert card", C_BAD);
        } else {
            setRow(R_SIM, reply.length() ? firstLine(reply) : String("no answer"), C_WAIT);
        }
        break;
    }
    case 2: {   // operator name, shown in the network row by step 3
        command("AT+COPS?", reply);
        operatorName = quoted(lineStarting(reply, "+COPS:"));
        break;
    }
    case 3: {   // registration on 4G
        command("AT+CEREG?", reply);
        int n = fields(lineStarting(reply, "+CEREG:"), f, 20);
        int stat = n >= 2 ? f[1].toInt() : -1;
        String op;
        if (operatorName.length()) {
            op = ", " + operatorName;
        }
        if (stat == 1) {
            setRow(R_NETWORK, "registered" + op, C_OK);
        } else if (stat == 5) {
            setRow(R_NETWORK, "roaming" + op, C_OK);
        } else if (stat == 2) {
            setRow(R_NETWORK, "searching...", C_WAIT);
        } else if (stat == 3) {
            setRow(R_NETWORK, "refused by the network", C_BAD);
        } else if (stat == 0) {
            setRow(R_NETWORK, "not searching", C_BAD);
        } else {
            setRow(R_NETWORK, "unknown", C_WAIT);
        }
        break;
    }
    case 4: {   // VoLTE
        command("AT+CIREG?", reply);
        int n = fields(lineStarting(reply, "+CIREG:"), f, 20);
        if (n >= 2 && f[1].toInt() == 1) {
            setRow(R_VOLTE, "yes: calls go over 4G", C_OK);
        } else {
            setRow(R_VOLTE, "not registered yet", C_WAIT);
        }
        break;
    }
    case 5: {   // 4G signal
        command("AT+CPSI?", reply);
        String line = lineStarting(reply, "+CPSI:");
        int n = fields(line, f, 20);
        lteNow = n > 0 && f[0].startsWith("LTE");
        if (lteNow && n >= 5) {
            int band = -1;
            for (int i = 0; i < n; i++) {
                int at = f[i].indexOf("BAND");
                if (at >= 0) {
                    band = f[i].substring(at + 4).toInt();
                }
            }
            int dbm = rsrpDbm(f[n - 3].toInt());
            char buf[60];
            snprintf(buf, sizeof buf, "%d dBm, %s, B%d", dbm, rsrpWord(dbm), band);
            setRow(R_SIGNAL, buf, dbm >= -100 ? C_OK : C_WAIT);
            addRsrp(band, dbm);
        } else if (n > 0 && f[0].startsWith("GSM")) {
            setRow(R_SIGNAL, "on 2G, not 4G", C_WAIT);
        } else if (n > 0) {
            setRow(R_SIGNAL, f[0], C_BAD);           // e.g. NO SERVICE
        } else {
            setRow(R_SIGNAL, "no answer", C_WAIT);
        }
        break;
    }
    case 6: {   // the modem's own battery reading
        if (command("AT+CBC", reply)) {
            String line = lineStarting(reply, "+CBC:");
            modemVolts = line.substring(line.indexOf(':') + 1).toFloat();
        }
        break;
    }
    case 7: {   // GPS: only whether it has a fix, never the position
        if (!gpsReady && millis() - gpsStartedAt > GPS_RETRY_MS) {
            command("AT+CGNSSPWR=0", reply);       // as on the bench: off and on again when READY doesn't come
            command("AT+CGNSSPWR=1", reply);
            gpsStartedAt = millis();
        }
        bool ok = command("AT+CGNSSINFO", reply);
        String line = lineStarting(reply, "+CGNSSINFO:");
        if (!ok || line.length() == 0) {
            setRow(R_GPS, "starting...", C_WAIT);
            break;
        }
        gpsReady = true;
        int n = fields(line, f, 20);
        int satellites = 0;
        bool fix = false;
        for (int i = 1; i < n; i++) {
            if (f[i].indexOf('.') >= 0) {
                fix = true;                         // the latitude: the satellite counts come before it
                break;
            }
            satellites += f[i].toInt();
        }
        if (fix) {
            setRow(R_GPS, "fix, " + String(satellites) + " satellites", C_OK);
        } else {
            setRow(R_GPS, "searching (no fix yet)", C_WAIT);
        }
        break;
    }
    }
    step = (step + 1) % 8;
}

// ---- the T-Deck's speaker (in the right-side grille): beeps, to test it and as the ringtone
constexpr int SPK_RATE = 16000;

void startSpeaker()
{
    i2s_config_t cfg = {};
    cfg.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_TX);
    cfg.sample_rate = SPK_RATE;
    cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_16BIT;
    cfg.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT;
    cfg.communication_format = I2S_COMM_FORMAT_STAND_I2S;
    cfg.dma_buf_count = 4;
    cfg.dma_buf_len = 256;
    cfg.tx_desc_auto_clear = true;
    i2s_pin_config_t pins = {};
    pins.mck_io_num = I2S_PIN_NO_CHANGE;
    pins.bck_io_num = PIN_SPK_BCK;
    pins.ws_io_num = PIN_SPK_WS;
    pins.data_out_num = PIN_SPK_DOUT;
    pins.data_in_num = I2S_PIN_NO_CHANGE;
    i2s_driver_install(I2S_NUM_0, &cfg, 0, nullptr);
    i2s_set_pin(I2S_NUM_0, &pins);
}

// A short beep: a 1 kHz tone, about a quarter of full volume.
void beep(int ms)
{
    static int16_t buf[2 * 64];
    int samples = SPK_RATE * ms / 1000;
    for (int done = 0; done < samples; done += 64) {
        for (int i = 0; i < 64; i++) {
            int16_t v = (int16_t)(8000 * sinf(2 * PI * 1000.0f * (done + i) / SPK_RATE));
            buf[2 * i] = buf[2 * i + 1] = v;
        }
        size_t written;
        i2s_write(I2S_NUM_0, buf, sizeof buf, &written, portMAX_DELAY);
    }
    i2s_zero_dma_buffer(I2S_NUM_0);
}

void ringBeeps()
{
    beep(150);
    delay(100);
    beep(150);
}

// ---- small helpers
float tdeckBatteryVolts()
{
    uint32_t sum = 0;
    for (int i = 0; i < 16; i++) {
        sum += analogReadMilliVolts(PIN_BATTERY);
    }
    return sum / 16.0f * BATTERY_DIVIDER / 1000.0f;
}

// ---- start
void setup()
{
    pinMode(PIN_POWER_ON, OUTPUT);
    digitalWrite(PIN_POWER_ON, HIGH);          // peripherals, and the Grove 3.3 V the modem board's VDD needs

    Serial.begin(BAUD);
    Serial.setTxTimeoutMs(0);                  // don't wait for a Mac that isn't connected

    modem.setRxBufferSize(4096);
    modem.begin(BAUD, SERIAL_8N1, PIN_MODEM_RX, PIN_MODEM_TX);

    // the screen shares its SPI bus with the microSD card and the LoRa radio: keep those two quiet
    pinMode(PIN_SD_CS, OUTPUT);
    digitalWrite(PIN_SD_CS, HIGH);
    pinMode(PIN_RADIO_CS, OUTPUT);
    digitalWrite(PIN_RADIO_CS, HIGH);
    pinMode(PIN_TFT_CS, OUTPUT);
    digitalWrite(PIN_TFT_CS, HIGH);
    pinMode(PIN_SPI_MISO, INPUT_PULLUP);
    SPI.begin(PIN_SPI_SCK, PIN_SPI_MISO, PIN_SPI_MOSI);

    tft.begin();
    for (auto &c : LCD_INIT) {
        tft.writecommand(c.cmd);
        for (int j = 0; j < (c.len & 0x7f); j++) {
            tft.writedata(c.data[j]);
        }
        if (c.len & 0x80) {
            delay(120);
        }
    }
    tft.setRotation(1);
    pinMode(PIN_BACKLIGHT, OUTPUT);
    digitalWrite(PIN_BACKLIGHT, HIGH);        // full brightness

    for (int r = 0; r < ROWS; r++) {
        setRow((Row)r, "-", C_DIM);
    }
    setRow(R_MODEM, "looking for it...", C_WAIT);
    setRow(R_CALL, "none", C_DIM);
    setRow(R_SMS, "none new", C_DIM);
    drawFrame();
    drawRows();

    startSpeaker();
    ringBeeps();                               // the speaker test: two beeps at start

    Serial.println();
    Serial.println("T-Deck phone test program. Anything you type goes straight to the modem.");
    Serial.println("Try: AT, AT+CPSI?, AT+CBC, ATD+91XXXXXXXXXX; (a call), AT+CHUP (hang up).");
}

void loop()
{
    static uint32_t lastAsk = 0, lastBattery = 0, lastDraw = 0;

    pumpUsb();
    pumpModem();

    if (!terminalBusy() && millis() - lastAsk >= POLL_EVERY_MS) {
        lastAsk = millis();
        askModem();
    }

    if (millis() - lastBattery >= 2000) {
        lastBattery = millis();
        char buf[60];
        if (modemVolts > 0) {
            snprintf(buf, sizeof buf, "%.2f V (modem %.2f V)", tdeckBatteryVolts(), modemVolts);
        } else {
            snprintf(buf, sizeof buf, "%.2f V", tdeckBatteryVolts());
        }
        setRow(R_BATTERY, buf, C_INFO);
    }

    if (ringPending) {
        ringPending = false;
        ringBeeps();
    }
    if (callShownAt && millis() - callShownAt > 15000) {
        setRow(R_CALL, "none", C_DIM);
        callShownAt = 0;
    }
    if (terminalBusy()) {
        uint32_t left = (TERMINAL_PAUSE_MS - (millis() - lastTyped)) / 1000 + 1;
        setRow(R_MAC, "in use: paused " + String(left) + " s", C_WAIT);
    } else {
        setRow(R_MAC, typedEver ? "terminal idle" : "no terminal yet", C_DIM);
    }

    if (millis() - lastDraw >= 150) {
        lastDraw = millis();
        drawRows();
    }
}
