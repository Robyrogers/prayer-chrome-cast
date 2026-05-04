package prayer

import (
	"fmt"
	"strconv"
	"strings"
)

func ParseTime(timeStr string) (PrayerTime, error) {
	parts := strings.Split(timeStr, " ")
	timePart := parts[0]
	
	hhMm := strings.Split(timePart, ":")
	if len(hhMm) != 2 {
		return PrayerTime{}, fmt.Errorf("invalid time format: %s", timeStr)
	}

	hh, err := strconv.Atoi(hhMm[0])
	if err != nil {
		return PrayerTime{}, err
	}

	mm, err := strconv.Atoi(hhMm[1])
	if err != nil {
		return PrayerTime{}, err
	}

	if len(parts) == 2 {
		amPm := strings.ToLower(parts[1])
		if amPm == "am" {
			if hh == 12 {
				hh = 0
			}
		} else if amPm == "pm" {
			if hh != 12 {
				hh += 12
			}
		}
	}

	return PrayerTime{Hour: hh, Minute: mm}, nil
}
