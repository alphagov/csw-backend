CREATE TABLE IF NOT EXISTS product_team_user(
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    team_id INTEGER NOT NULL,
    CONSTRAINT "product_team_user_user_id_fkey" FOREIGN KEY (user_id)
      REFERENCES  "user" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION,
    CONSTRAINT "product_team_user_team_id_fkey" FOREIGN KEY (team_id)
      REFERENCES "product_team" (id) MATCH SIMPLE
      ON UPDATE NO ACTION ON DELETE NO ACTION
);
