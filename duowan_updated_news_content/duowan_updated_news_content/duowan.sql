CREATE DATABASE t_duowan_news DEFAULT CHARACTER SET utf8 COLLATE utf8_general_ci;
CREATE TABLE `t_duowan_news` (
  `linkmd5id` char(32) NOT NULL COMMENT 'url md5编码id',
  `title` text COMMENT '标题',
  `date` int(10) COMMENT '日期',
  `link` text  COMMENT 'url链接',
  `content` blob COMMENT '内容',
  `updated` datetime DEFAULT NULL  COMMENT '最后更新时间',
  PRIMARY KEY (`linkmd5id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;