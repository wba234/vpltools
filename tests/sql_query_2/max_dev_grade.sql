SELECT climber_first_name, climber_last_name, grade_str AS "YDS Grade"
  FROM (
      SELECT climber_first_name, climber_last_name, MAX(grade_id) AS max_grade
        FROM climbers
            INNER JOIN climber_climbs_established USING (climber_id)
            INNER JOIN climbs USING (climb_id)
            INNER JOIN climb_grades USING (grade_id)
      GROUP BY climber_id
  ) AS max_grade_subqry
      INNER JOIN climb_grades ON grade_id = max_grade;