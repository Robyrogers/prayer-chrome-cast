package prayer

import (
)

type PrayerTime struct {
	Hour   int `json:"hh"`
	Minute int `json:"mm"`
}

type APIResponse struct {
	Code int `json:"code"`
	Data struct {
		Timings map[string]string `json:"timings"`
	} `json:"data"`
}

type PrayerSchedule struct {
	City    string
	Country string
}

func NewPrayerSchedule(city, country string) *PrayerSchedule {
	return &PrayerSchedule{
		City:    city,
		Country: country,
	}
}
