-- 001_init.sql
-- MySQL 8.x / InnoDB / utf8mb4

SET NAMES utf8mb4;

-- 1. 用户
CREATE TABLE `user` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '用户唯一标识',
  `username` VARCHAR(50) NOT NULL COMMENT '登录名，不可重复',
  `password` VARCHAR(255) NOT NULL COMMENT '密码哈希，不存明文',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '注册时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_user_username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='用户';

-- 2. 视频文档
CREATE TABLE `video` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '视频记录唯一标识',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '哪个用户导入的',
  `bvid` VARCHAR(50) NOT NULL COMMENT 'B站视频号',
  `title` VARCHAR(255) NOT NULL COMMENT '视频标题',
  `cid` VARCHAR(50) NULL COMMENT 'B站分P标识，备用',
  `subtitle_json` MEDIUMTEXT NULL COMMENT '完整字幕数组（JSON）',
  `status` VARCHAR(20) NOT NULL DEFAULT 'IMPORTING' COMMENT 'IMPORTING / SUCCESS / FAILED',
  `is_pinned` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '是否置顶：0=否，1=是',
  `fail_reason` VARCHAR(500) NULL COMMENT '失败原因，成功时为空',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '导入时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_video_user_bvid` (`user_id`, `bvid`),
  CONSTRAINT `fk_video_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_video_status` CHECK (`status` IN ('IMPORTING', 'SUCCESS', 'FAILED'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='视频文档';

-- 3. 对话
CREATE TABLE `conversation` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '对话唯一标识',
  `video_id` BIGINT UNSIGNED NOT NULL COMMENT '哪个视频下的对话',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '对话创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_conversation_video_id` (`video_id`),
  CONSTRAINT `fk_conversation_video` FOREIGN KEY (`video_id`) REFERENCES `video` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='对话';

-- 4. 消息
CREATE TABLE `message` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '消息唯一标识',
  `conversation_id` BIGINT UNSIGNED NOT NULL COMMENT '挂在哪个对话下',
  `role` VARCHAR(20) NOT NULL COMMENT 'user 或 assistant',
  `content` MEDIUMTEXT NOT NULL COMMENT '消息内容',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '发送时间',
  PRIMARY KEY (`id`),
  KEY `idx_message_conversation_id` (`conversation_id`),
  CONSTRAINT `fk_message_conversation` FOREIGN KEY (`conversation_id`) REFERENCES `conversation` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_message_role` CHECK (`role` IN ('user', 'assistant'))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='消息';

-- 5. 生词
CREATE TABLE `word` (
  `id` BIGINT UNSIGNED NOT NULL AUTO_INCREMENT COMMENT '生词唯一标识',
  `user_id` BIGINT UNSIGNED NOT NULL COMMENT '哪个用户的生词',
  `word` VARCHAR(100) NOT NULL COMMENT '单词',
  `is_reviewed` TINYINT(1) NOT NULL DEFAULT 0 COMMENT '0=未复习，1=已复习',
  `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP COMMENT '添加时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `uk_word_user_word` (`user_id`, `word`),
  CONSTRAINT `fk_word_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `chk_word_is_reviewed` CHECK (`is_reviewed` IN (0, 1))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci COMMENT='生词';