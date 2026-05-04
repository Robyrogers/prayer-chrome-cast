package prayer

import (
	"encoding/json"
	"fmt"
	"net/http"
	"time"
)

func (ps *PrayerSchedule) GetTimings(dateStr string) (map[string]PrayerTime, error) {
	if dateStr == "" {
		dateStr = time.Now().Format("02-01-2006")
	}

	url := fmt.Sprintf("http://api.aladhan.com/v1/timingsByCity/%s?city=%s&country=%s&method=3", 
		dateStr, ps.City, ps.Country)

	resp, err := http.Get(url)
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	var apiResp APIResponse
	if err := json.NewDecoder(resp.Body).Decode(&apiResp); err != nil {
		return nil, err
	}

	if apiResp.Code != 200 {
		return nil, fmt.Errorf("API returned code %d", apiResp.Code)
	}

	prayers := []string{"Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"}
	result := make(map[string]PrayerTime)

	for _, p := range prayers {
		timeStr, ok := apiResp.Data.Timings[p]
		if !ok {
			return nil, fmt.Errorf("prayer %s not found in response", p)
		}
		pt, err := ParseTime(timeStr)
		if err != nil {
			return nil, fmt.Errorf("error parsing time for %s: %v", err)
		}
		result[p] = pt
	}

	return result, nil
}
