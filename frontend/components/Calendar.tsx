// components/Calendar.tsx
"use client"

import React, { useState, useEffect } from 'react';
import moment, { Moment } from 'moment';
import styles from './Calendar.module.css';

interface HighlightedDays {
  [key: string]: 'red' | 'green' | 'blue' | 'yellow' | undefined;
}

const Calendar: React.FC = () => {
  const year = 2025; // Example year
  const startOfYear = moment(`${year}-01-01`);
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  // Create a 2D array where each sub-array holds the days for a specific month
  const daysInMonths = months.map((_, monthIndex) => {
    const startOfMonth = moment(`${year}-${monthIndex + 1}-01`);
    const daysInMonth = Array.from({ length: startOfMonth.daysInMonth() }, (_, i) =>
      startOfMonth.clone().add(i, 'days')
    );
    return daysInMonth;
  });

  // State to hold the highlighted colors for each day
  const [highlightedDays, setHighlightedDays] = useState<HighlightedDays>({});
  const [apiDates, setApiDates] = useState<string[]>([]); // State to store dates from the API

  // Fetch the list of dates from the API when the component mounts
  useEffect(() => {
    const fetchApiDates = async () => {
      try {
        const response = await fetch('http://localhost:8000/workout-dates');
        const data = await response.json();
        // Assuming the API returns an array of date strings like ["2024-02-01", "2024-03-15"]
        setApiDates(data);
      } catch (error) {
        console.error('Error fetching dates from API:', error);
      }
    };

    fetchApiDates();
  }, []); // Empty dependency array means this runs once when the component mounts

  // Function to check if a day is in the API list of dates
  const isDateInApiList = (day: Moment): boolean => {
    const dayString = day.format('YYYY-MM-DD');
    return apiDates.includes(dayString);
  };

  const handleDayClick = (day: Moment) => {
    // Toggle between colors for highlighting (e.g., red, green, blue)
    const colors: ('red' | 'green' | 'blue' | 'yellow')[] = ['red', 'green', 'blue', 'yellow'];
    const currentColor = highlightedDays[day.format('YYYY-MM-DD')];
    const nextColor = colors[(colors.indexOf(currentColor ?? 'red') + 1) % colors.length];
    
    setHighlightedDays((prev) => ({
      ...prev,
      [day.format('YYYY-MM-DD')]: nextColor,
    }));
  };

  return (
    <div className={styles.calendarContainer}>
      {months.map((monthName, index) => (
        <div key={monthName} className={styles.monthColumn}>
          <h3 className={styles.monthLabel}>{monthName}</h3>
          <div className={styles.daysGrid}>
            {daysInMonths[index].map((day) => {
              const dayString = day.format('YYYY-MM-DD');
              const isHighlighted = highlightedDays[dayString];
              const isApiDate = isDateInApiList(day); // Check if the day is in the API list

              return (
                <div
                  key={dayString}
                  className={`${styles.day} ${isHighlighted ? styles[isHighlighted] : ''} ${isApiDate ? styles.green : ''}`} // Add green class if the date is in the API list
                  onClick={() => handleDayClick(day)}
                >
                  {day.format('D')}
                </div>
              );
            })}
          </div>
        </div>
      ))}
    </div>
  );
};

export default Calendar;
