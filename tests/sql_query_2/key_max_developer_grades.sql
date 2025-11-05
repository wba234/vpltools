-- 11. Show the maximum grade (e.g. "5.11b") established by each developer. 
--     Each developer should appear only once. Show the first and last names
--     of each developer, along with the grade string of the maximum grade 
--     they have established.
SELECT climber_first_name, climber_last_name, grade_str
  FROM (
      SELECT climber_first_name, climber_last_name, MAX(grade_id) AS max_grade
        FROM climbers
            INNER JOIN climber_climbs_established USING (climber_id)
            INNER JOIN climbs USING (climb_id)
            INNER JOIN climb_grades USING (grade_id)
      GROUP BY climber_id
  ) AS max_grade_subqry
      INNER JOIN climb_grades ON max_grade_subqry.max_grade = grade_id;