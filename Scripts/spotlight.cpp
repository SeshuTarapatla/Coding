#include <iostream>
#include <string>
#include <filesystem>
#include <ctime>
#include <algorithm>
#include <vector>
#include <fstream>
#include <iomanip>
#include <sstream>
#include <windows.h>
#include <shlobj.h>
#include <opencv2/opencv.hpp>
#include <openssl/md5.h>

namespace fs = std::filesystem;

// ANSI color codes for console output
const std::string BLUE = "\033[1;34m";
const std::string RED = "\033[1;31m";
const std::string RESET = "\033[0m";

// Get environment variable helper function
std::string getEnvVar(const char* varName) {
    char* buf = nullptr;
    size_t sz = 0;
    if (_dupenv_s(&buf, &sz, varName) == 0 && buf != nullptr) {
        std::string ret(buf);
        free(buf);
        return ret;
    }
    return "";
}

// Logging functions
void logInfo(const std::string& message) {
    std::cout << "[" << BLUE << "INFO" << RESET << "] " << message << std::endl;
}

void logError(const std::string& message) {
    std::cout << "[" << RED << "ERROR" << RESET << "] " << message << std::endl;
}

// Generate MD5 hash of an image
std::string generateHash(const std::string& filepath) {
    try {
        logInfo("Generating Hash for \"" + fs::path(filepath).filename().string() + "\"");
        
        cv::Mat img = cv::imread(filepath);
        if (img.empty()) {
            throw std::runtime_error("Failed to load image");
        }

        MD5_CTX md5Context;
        MD5_Init(&md5Context);
        MD5_Update(&md5Context, img.data, img.total() * img.elemSize());
        
        unsigned char result[MD5_DIGEST_LENGTH];
        MD5_Final(result, &md5Context);

        std::stringstream ss;
        for (int i = 0; i < MD5_DIGEST_LENGTH; i++) {
            ss << std::hex << std::setw(2) << std::setfill('0') << static_cast<int>(result[i]);
        }
        
        return ss.str();
    }
    catch (const std::exception& e) {
        logError("FileNotFound: \"" + filepath + "\"");
        return "";
    }
}

class Spotlite {
private:
    fs::path destinationDirectory;
    std::string date;
    int index;
    const std::string prefix = "Windows-Spotlight";
    std::string lastWallpaper;

    std::string getCurrentDate() {
        time_t now = time(0);
        tm ltm;
        localtime_s(&ltm, &now);
        std::stringstream ss;
        ss << std::setw(4) << (ltm.tm_year + 1900) << "-"
           << std::setw(2) << std::setfill('0') << (ltm.tm_mon + 1) << "-"
           << std::setw(2) << std::setfill('0') << ltm.tm_mday;
        return ss.str();
    }

    std::string fetchLastWallpaper() {
        std::vector<std::string> files;
        for (const auto& entry : fs::directory_iterator(destinationDirectory)) {
            if (entry.path().filename().string().find(prefix) == 0) {
                files.push_back(entry.path().string());
            }
        }
        
        if (files.empty()) {
            throw std::runtime_error("No existing wallpapers found");
        }
        
        std::sort(files.begin(), files.end(), std::greater<std::string>());
        return files[0];
    }

    std::string generateOutputFilename() {
        while (true) {
            std::stringstream ss;
            ss << destinationDirectory.string() << "\\" 
               << prefix << "-" << date << "_"
               << std::setw(2) << std::setfill('0') << index << ".jpg";
            
            if (!fs::exists(ss.str())) {
                return ss.str();
            }
            index++;
        }
    }

    void checkDuplicate(const std::string& sourceFile) {
        std::string hash1 = generateHash(sourceFile);
        std::string hash2 = generateHash(lastWallpaper);

        if (hash1 == hash2) {
            logInfo("Hashes match (hash1: " + hash1 + ", hash2: " + hash2 + ")");
            throw std::runtime_error("File already exists");
        }
        else {
            logInfo("Hashes don't match (hash1: " + hash1 + ", hash2: " + hash2 + ")");
        }
    }

public:
    Spotlite() : index(1) {
        std::string appdata = getEnvVar("APPDATA");
        std::string userProfile = getEnvVar("USERPROFILE");
        
        std::string sourceFile = appdata + "\\Microsoft\\Windows\\Themes\\TranscodedWallpaper";
        destinationDirectory = fs::path(userProfile + "\\Pictures\\Windows Spotlight");

        fs::create_directories(destinationDirectory);
        date = getCurrentDate();
        lastWallpaper = fetchLastWallpaper();
    }

    void fetchCurrentWallpaper() {
        try {
            std::string sourceFile = getEnvVar("APPDATA") + 
                "\\Microsoft\\Windows\\Themes\\TranscodedWallpaper";
            
            checkDuplicate(sourceFile);
            std::string output = generateOutputFilename();
            fs::copy_file(sourceFile, output, fs::copy_options::none);
            logInfo("Wallpaper copied: \"" + fs::path(output).filename().string() + "\"");
        }
        catch (const std::runtime_error& e) {
            logInfo("Wallpaper already copied.");
        }
        catch (const std::exception& e) {
            logError(e.what());
        }
    }
};

int main() {
    // Enable ANSI escape sequences in Windows console
    HANDLE hOut = GetStdHandle(STD_OUTPUT_HANDLE);
    DWORD dwMode = 0;
    GetConsoleMode(hOut, &dwMode);
    SetConsoleMode(hOut, dwMode | ENABLE_VIRTUAL_TERMINAL_PROCESSING);

    try {
        Spotlite spotlite;
        spotlite.fetchCurrentWallpaper();
    }
    catch (const std::exception& e) {
        logError(e.what());
        return 1;
    }

    return 0;
}
