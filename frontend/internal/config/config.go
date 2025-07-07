package config

import (
	"os"
	"strconv"
)

type Config struct {
	Port       string
	BackendURL string
	Debug      bool
}

func Load() *Config {
	debug, _ := strconv.ParseBool(os.Getenv("DEBUG"))
	if debug == false {
		debug, _ = strconv.ParseBool(os.Getenv("GIN_MODE"))
	}

	return &Config{
		Port:       getEnv("GO_PORT", "8080"),
		BackendURL: getEnv("BACKEND_URL", "http://localhost:8000"),
		Debug:      debug,
	}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}