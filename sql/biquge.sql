CREATE TABLE "fiction_list" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "fiction_code" TEXT NOT NULL,
  "fiction_name" TEXT,
  "fiction_info" TEXT,
  "fiction_introduce" TEXT,
  "fiction_author" TEXT,
  "fiction_type" TEXT,
  "fiction_image_url" TEXT,
  "fiction_count" TEXT,
  "create_time" DATE,
  "update_time" DATE
);
CREATE TABLE "chapter_list" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "fiction_code" TEXT NOT NULL,
  "chapter_code" TEXT NOT NULL,
  "chapter_name" TEXT NOT NULL,
  "chapter_order" INTEGER NOT NULL DEFAULT 0,
  "create_time" DATE,
  "update_time" DATE
);
CREATE TABLE biquge_list (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    each_code TEXT,
    each_type TEXT,
    each_href TEXT,
    each_title TEXT,
    each_author TEXT,
    each_update_time TEXT,
    page_info TEXT,
    now_time TEXT
);
CREATE TABLE "chapter_detail_list" (
  "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
  "chapter_code" TEXT NOT NULL,
  "chapter_content" TEXT NOT NULL
);
