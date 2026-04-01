//
// Created by Kali Banghart on 2/28/26.
//

#ifndef M1AP_JSON_H
#define M1AP_JSON_H
#pragma once
#include <string>
#include <unordered_map>
#include <sstream>
#include <fstream>
#include <cctype>

// Minimal JSON parser/writer for pet state communication.
// Only handles flat objects
// Learned this from hackathon
namespace sjson {

// a single JSON value - number, string, bool, or null
struct Value {
    enum class Type { Number, String, Bool, Null } type = Type::Null;
    double num = 0.0;
    bool b     = false;
    std::string s;

    static Value number (double x)             { Value v; v.type = Type::Number; v.num = x; return v; }
    static Value str    (const std::string& x) { Value v; v.type = Type::String; v.s   = x; return v; }
    static Value boolean(bool x)               { Value v; v.type = Type::Bool;   v.b   = x; return v; }
};

using Obj = std::unordered_map<std::string, Value>;

inline std::string trim(const std::string& in) {
    size_t a = 0, b = in.size();
    while (a < b && std::isspace(static_cast<unsigned char>(in[a])))   a++;
    while (b > a && std::isspace(static_cast<unsigned char>(in[b-1]))) b--;
    return in.substr(a, b - a);
}

inline bool parse(const std::string& text, Obj& out) {
    out.clear();
    std::string t = trim(text);
    if (t.size() < 2 || t.front() != '{' || t.back() != '}') return false;

    size_t i = 1;

    auto skip_ws = [&]() {
        while (i < t.size() && std::isspace(static_cast<unsigned char>(t[i]))) i++;
    };

    auto parse_string = [&]() -> std::string {
        std::string r;
        if (t[i] != '"') return r;
        i++;
        while (i < t.size() && t[i] != '"') {
            if (t[i] == '\\' && i + 1 < t.size()) {
                i++;
                r.push_back(t[i]);
                i++;
            } else {
                r.push_back(t[i]);
                i++;
            }
        }
        if (i < t.size() && t[i] == '"') i++;
        return r;
    };

    auto parse_number = [&]() -> double {
        size_t start = i;
        while (i < t.size() && (std::isdigit(static_cast<unsigned char>(t[i])) || t[i] == '-' || t[i] == '.')) i++;
        return std::stod(t.substr(start, i - start));
    };

    while (i < t.size()) {
        skip_ws();
        if (i < t.size() && t[i] == '}') break;

        if (i >= t.size() || t[i] != '"') return false;
        std::string key = parse_string();
        skip_ws();
        if (i >= t.size() || t[i] != ':') return false;
        i++;
        skip_ws();

        if (i >= t.size()) return false;
        if (t[i] == '"') {
            out[key] = Value::str(parse_string());
        } else if (std::isdigit(static_cast<unsigned char>(t[i])) || t[i] == '-') {
            out[key] = Value::number(parse_number());
        } else if (t.compare(i, 4, "true") == 0) {
            i += 4;
            out[key] = Value::boolean(true);
        } else if (t.compare(i, 5, "false") == 0) {
            i += 5;
            out[key] = Value::boolean(false);
        } else {
            return false;
        }

        skip_ws();
        if (i < t.size() && t[i] == ',') { i++; continue; }
        if (i < t.size() && t[i] == '}') break;
    }
    return true;
}

// escape special characters for JSON output
inline std::string escape(const std::string& s) {
    std::string r;
    for (char c : s) {
        if (c == '"' || c == '\\') r.push_back('\\');
        r.push_back(c);
    }
    return r;
}

inline std::string dump(const Obj& obj) {
    std::ostringstream oss;
    oss << "{";
    bool first = true;
    for (const auto& [k, v] : obj) {
        if (!first) oss << ",";
        first = false;
        oss << "\"" << escape(k) << "\":";
        if      (v.type == Value::Type::String) oss << "\"" << escape(v.s) << "\"";
        else if (v.type == Value::Type::Number) oss << v.num;
        else if (v.type == Value::Type::Bool)   oss << (v.b ? "true" : "false");
        else                                    oss << "null";
    }
    oss << "}";
    return oss.str();
}

inline bool read_file(const std::string& path, std::string& out) {
    std::ifstream in(path);
    if (!in) return false;
    std::ostringstream ss;
    ss << in.rdbuf();
    out = ss.str();
    return true;
}

inline bool write_file(const std::string& path, const std::string& text) {
    std::ofstream out(path);
    if (!out) return false;
    out << text;
    return true;
}

// safely read typed values with a fallback default
inline double get_num(const Obj& o, const std::string& k, double def) {
    auto it = o.find(k);
    if (it == o.end() || it->second.type != Value::Type::Number) return def;
    return it->second.num;
}

inline bool get_bool(const Obj& o, const std::string& k, bool def) {
    auto it = o.find(k);
    if (it == o.end() || it->second.type != Value::Type::Bool) return def;
    return it->second.b;
}

inline std::string get_str(const Obj& o, const std::string& k, const std::string& def) {
    auto it = o.find(k);
    if (it == o.end() || it->second.type != Value::Type::String) return def;
    return it->second.s;
}

} // namespace sjson

#endif // M1AP_JSON_H