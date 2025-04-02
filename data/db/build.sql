CREATE TABLE IF NOT EXISTS guilds (
	guild_id integer PRIMARY KEY,
	prefix text DEFAULT "s!"
);




CREATE TABLE IF NOT EXISTS threat (
    user_id integer,
    username text,
    positivos integer,
    potencial integer,
    linkscan text,
    arquivo_link text
);


CREATE TABLE IF NOT EXISTS mutes (
    user_id integer,
    guild_id integer,
    role_ids text,
    end_time text,
    role_mute integer
);


CREATE TABLE IF NOT EXISTS users  (
    user_id integer PRIMARY KEY,
    avatar text DEFAULT NULL,
    bg_image text DEFAULT NULL,
    about text DEFAULT NULL,
    badges text DEFAULT NULL,
    coins float DEFAULT 0.0
);

CREATE TABLE IF NOT EXISTS characters (
    id integer PRIMARY KEY,
    user_id integer,
    username text,
    kingdom integer,
    sex integer,
    avatar integer,
    race integer,
    guild_id integer DEFAULT NULL,
    xp float DEFAULT 0.0,
    level integer DEFAULT 0,
    pets text DEFAULT NULL,
    quests text DEFAULT NULL,
    q_completed text DEFAULT NULL,
    inventory text DEFAULT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE IF NOT EXISTS items (
    id integer PRIMARY KEY,
    name text,
    icon text,
    description text,
    type integer,
    attributes text
);


CREATE TABLE IF NOT EXISTS quests (
    id integer PRIMARY KEY,
    name text,
    description text,
    lore text,
    rank text,
    rewards text,
    bonus text 
);

CREATE TABLE IF NOT EXISTS pets (
    id integer PRIMARY KEY,
    name text,
    health float,
    avatar integer,
    race integer,
    bonus text
);

CREATE TABLE IF NOT EXISTS pets_user (
    id integer PRIMARY KEY,
    user_id integer,
    name text,
    health float, 
    avatar text,
    pet_id integer,
    bonus text,
    FOREIGN KEY (pet_id) REFERENCES pets(id)
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

