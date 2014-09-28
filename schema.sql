drop table if exists requests;
create table requests (
  id integer primary key autoincrement,
  userID integer not null,
  courseID integer not null,
  unixTime integer not null,
  location text not null,
  offer text not null,
  description text not null
);

drop table if exists courses;
create table courses (
  id integer primary key autoincrement,
  code text not null
);

drop table if exists users;
create table users (
  id integer primary key autoincrement,
  userName text not null,
  hashedPass text not null,
  fullName text not null
);

drop table if exists userCourses;
create table userCourses (
  userID integer not null,
  courseID integer not null
);

INSERT INTO users (userName,hashedPass,fullName) VALUES ("lbr58@cornell.edu","securepass","Logan Rosen");
INSERT INTO users (userName,hashedPass,fullName) VALUES ("jz479@cornell.edu","notsecurepass","Jeff Zhou");
INSERT INTO users (userName,hashedPass,fullName) VALUES ("nec45@cornell.edu","sucks","Nicole Calace");

INSERT INTO courses (code) VALUES ("CS 1110");
INSERT INTO courses (code) VALUES ("CS 2850");
INSERT INTO courses (code) VALUES ("INFO 2310");
INSERT INTO courses (code) VALUES ("DEA 1500");

INSERT INTO requests (userID,courseID,unixTime,location,offer,description) VALUES (1,1,1411838730,"West Campus","$5.21","HALP!!!");
INSERT INTO requests (userID,courseID,unixTime,location,offer,description) VALUES (2,1,1410838730,"North Campus","£250","help meeeeee!");
INSERT INTO requests (userID,courseID,unixTime,location,offer,description) VALUES (3,3,1401388330,"Central Campus","326¥","I suck");

INSERT INTO userCourses (userID,courseID) VALUES (1,1);
INSERT INTO userCourses (userID,courseID) VALUES (1,2);
INSERT INTO userCourses (userID,courseID) VALUES (3,3);
INSERT INTO userCourses (userID,courseID) VALUES (4,4);
