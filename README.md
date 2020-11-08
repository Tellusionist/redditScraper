# redditScraper
A reddit scraper that sends custom notifications based on post titles


sqlite code snippets
`create table if not exists posts ( subreddit text, post_id text, created integer, flair text, title text, flg_player integer, flg_5e interger, flg_pbp integer, url text);`