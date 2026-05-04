package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"prayer-cli/internal/prayer"
)

func main() {
	if len(os.Args) < 2 {
		printUsage()
		os.Exit(1)
	}

	cmd := os.Args[1]
	switch cmd {
	case "timings":
		handleTimings()
	default:
		fmt.Printf("Unknown command: %s\n", cmd)
		printUsage()
		os.Exit(1)
	}
}

func printUsage() {
	fmt.Println("Usage: prayer-cli <command> [options]")
	fmt.Println("Commands:")
	fmt.Println("  timings   Fetch prayer timings")
	fmt.Println("Options for timings:")
	fmt.Println("  -city     City name (required)")
	fmt.Println("  -country   Country name (required)")
	fmt.Println("  -date      Date in dd-mm-yyyy format (optional)")
}

func handleTimings() {
	fs := flag.NewFlagSet("timings", flag.ContinueOnError)
	
	city := fs.String("city", "", "City name")
	country := fs.String("country", "", "Country name")
	date := fs.String("date", "", "Date in dd-mm-yyyy format")

	if err := fs.Parse(os.Args[2:]); err != nil {
		fmt.Println("Error parsing flags:", err)
		os.Exit(1)
	}

	if *city == "" || *country == "" {
		fmt.Println("Error: -city and -country are required")
		fs.Usage()
		os.Exit(1)
	}

	schedule := prayer.NewPrayerSchedule(*city, *country)
	timings, err := schedule.GetTimings(*date)
	if err != nil {
		fmt.Printf("Error fetching timings: %v\n", err)
		os.Exit(1)
	}

	output, err := json.MarshalIndent(timings, "", "  ")
	if err != nil {
		fmt.Printf("Error encoding JSON: %v\n", err)
		os.Exit(1)
	}

	fmt.Println(string(output))
}
