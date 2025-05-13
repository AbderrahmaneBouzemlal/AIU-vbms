BEGIN;
--
-- Create model Venue
--
CREATE TABLE `venue` (
  `id` int NOT NULL AUTO_INCREMENT,
  `name` varchar(100) NOT NULL,
  `description` text DEFAULT NULL,
  `capacity` int NOT NULL,
  `location` varchar(200) NOT NULL,
  `category` varchar(50) DEFAULT NULL,
  `handled_by` varchar(255) NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `requires_approval` tinyint(1) NOT NULL,
  `requires_payment` tinyint(1) NOT NULL,
  `requires_documents` tinyint(1) NOT NULL,
  `features` text DEFAULT NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `venue_features_check` CHECK (json_valid(`features`) OR `features` IS NULL)
) ENGINE=InnoDB;

--
-- Create model VenueAvailability
--
CREATE TABLE `venue_availability` (
  `id` int NOT NULL AUTO_INCREMENT,
  `date` date NOT NULL,
  `start_time` time NOT NULL,
  `end_time` time NOT NULL,
  `is_available` tinyint(1) NOT NULL,
  `venue_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `venue_availability_venue_id_date_start_time_end_time_dc38011e_uniq` (`venue_id`,`date`,`start_time`,`end_time`),
  KEY `venue_availability_venue_id_89d52640` (`venue_id`),
  CONSTRAINT `venue_availability_venue_id_89d52640_fk_venue_id` FOREIGN KEY (`venue_id`) REFERENCES `venue` (`id`)
) ENGINE=InnoDB;

COMMIT;

BEGIN;
--
-- Create model UserProfile
--
CREATE TABLE `user_profile` (
  `id` int NOT NULL AUTO_INCREMENT,
  `profile_picture` varchar(100) NOT NULL,
  `bio` text DEFAULT NULL,
  `date_of_birth` date DEFAULT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `location` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB;

--
-- Create model User
--
CREATE TABLE `auth_user` (
  `id` int NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime NOT NULL,
  `email` varchar(254) NOT NULL,
  `first_name` varchar(100) NOT NULL,
  `last_name` varchar(100) NOT NULL,
  `user_type` varchar(20) NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `phone_number` varchar(20) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB;

CREATE TABLE `auth_user_groups` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `group_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_user_id_6a12ed8b` (`user_id`),
  KEY `auth_user_groups_group_id_97559544` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

CREATE TABLE `auth_user_user_permissions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` bigint NOT NULL,
  `permission_id` int NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permissions_user_id_a95ead1b` (`user_id`),
  KEY `auth_user_user_permissions_permission_id_1fbb5f2c` (`permission_id`),
  CONSTRAINT `auth_user_user_permissio_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

--
-- Create model AdminProfile
--
CREATE TABLE `admin_profile` (
  `userprofile_ptr_id` bigint NOT NULL,
  `admin_id` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`userprofile_ptr_id`),
  CONSTRAINT `admin_profile_userprofile_ptr_id_7c0f1a0a_fk_user_profile_id` FOREIGN KEY (`userprofile_ptr_id`) REFERENCES `user_profile` (`id`)
) ENGINE=InnoDB;

--
-- Create model StaffProfile
--
CREATE TABLE `staff_profile` (
  `userprofile_ptr_id` bigint NOT NULL,
  `staff_id` varchar(20) DEFAULT NULL,
  `department` varchar(100) DEFAULT NULL,
  `position` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`userprofile_ptr_id`),
  CONSTRAINT `staff_profile_userprofile_ptr_id_7f8c9f1e_fk_user_profile_id` FOREIGN KEY (`userprofile_ptr_id`) REFERENCES `user_profile` (`id`)
) ENGINE=InnoDB;

--
-- Create model StudentProfile
--
CREATE TABLE `student_profile` (
  `userprofile_ptr_id` bigint NOT NULL,
  `student_id` varchar(20) DEFAULT NULL,
  `major` varchar(100) DEFAULT NULL,
  `organization` varchar(100) DEFAULT NULL,
  `year` int NOT NULL,
  PRIMARY KEY (`userprofile_ptr_id`),
  CONSTRAINT `student_profile_userprofile_ptr_id_4e1a5a1e_fk_user_profi` FOREIGN KEY (`userprofile_ptr_id`) REFERENCES `user_profile` (`id`)
) ENGINE=InnoDB;

--
-- Add field user to userprofile
--
ALTER TABLE `user_profile` ADD COLUMN `user_id` bigint NOT NULL UNIQUE;
ALTER TABLE `user_profile` ADD CONSTRAINT `user_profile_user_id_3c5d6e1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`);

COMMIT;

BEGIN;
--
-- Create model Booking
--
CREATE TABLE `booking` (
  `id` int NOT NULL AUTO_INCREMENT,
  `booking_code` varchar(20) NOT NULL,
  `title` varchar(255) NOT NULL,
  `description` text NOT NULL,
  `start_time` datetime NOT NULL,
  `end_time` datetime NOT NULL,
  `attendees_count` int unsigned NOT NULL,
  `status` varchar(20) NOT NULL,
  `created_at` datetime NOT NULL,
  `updated_at` datetime NOT NULL,
  `payment_required` tinyint(1) NOT NULL,
  `payment_amount` decimal(10,2) DEFAULT NULL,
  `payment_completed` tinyint(1) NOT NULL,
  `payment_reference` varchar(100) NOT NULL,
  `requires_approval` tinyint(1) NOT NULL,
  `approval_date` datetime DEFAULT NULL,
  `documents_required` tinyint(1) NOT NULL,
  `documents_verified` tinyint(1) NOT NULL,
  `approved_by_id` bigint DEFAULT NULL,
  `user_id` bigint NOT NULL,
  `venue_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `booking_code` (`booking_code`),
  KEY `booking_status_b99f68_idx` (`status`),
  KEY `booking_user_id_acf7f7_idx` (`user_id`),
  KEY `booking_venue_i_1ab500_idx` (`venue_id`),
  KEY `booking_start_t_616860_idx` (`start_time`,`end_time`),
  KEY `booking_approved_by_id_30bf1330` (`approved_by_id`),
  KEY `booking_user_id_1bd7cb6e` (`user_id`),
  KEY `booking_venue_id_204dff63` (`venue_id`),
  CONSTRAINT `booking_approved_by_id_30bf1330_fk_auth_user_id` FOREIGN KEY (`approved_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `booking_user_id_1bd7cb6e_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `booking_venue_id_204dff63_fk_venue_id` FOREIGN KEY (`venue_id`) REFERENCES `venue` (`id`),
  CONSTRAINT `booking_attendees_count_check` CHECK (`attendees_count` >= 0)
) ENGINE=InnoDB;

--
-- Create model BookingFeedback
--
CREATE TABLE `booking_feedback` (
  `id` int NOT NULL AUTO_INCREMENT,
  `content` text NOT NULL,
  `is_internal` tinyint(1) NOT NULL,
  `feedback_type` varchar(50) NOT NULL,
  `created_at` datetime NOT NULL,
  `booking_id` bigint NOT NULL,
  `staff_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_feedback_booking_id_5b8eba55` (`booking_id`),
  KEY `booking_feedback_staff_id_6d3fc320` (`staff_id`),
  CONSTRAINT `booking_feedback_booking_id_5b8eba55_fk_booking_id` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`),
  CONSTRAINT `booking_feedback_staff_id_6d3fc320_fk_auth_user_id` FOREIGN KEY (`staff_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

--
-- Create model BookingFile
--
CREATE TABLE `booking_file` (
  `id` int NOT NULL AUTO_INCREMENT,
  `file` varchar(100) NOT NULL,
  `file_name` varchar(255) NOT NULL,
  `file_type` varchar(50) NOT NULL,
  `document_type` varchar(100) NOT NULL,
  `description` text NOT NULL,
  `uploaded_at` datetime NOT NULL,
  `is_verified` tinyint(1) NOT NULL,
  `verified_at` datetime DEFAULT NULL,
  `booking_id` bigint NOT NULL,
  `uploaded_by_id` bigint DEFAULT NULL,
  `verified_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_file_booking_id_fad8c254` (`booking_id`),
  KEY `booking_file_uploaded_by_id_c058674d` (`uploaded_by_id`),
  KEY `booking_file_verified_by_id_3e5fe9ef` (`verified_by_id`),
  CONSTRAINT `booking_file_booking_id_fad8c254_fk_booking_id` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`),
  CONSTRAINT `booking_file_uploaded_by_id_c058674d_fk_auth_user_id` FOREIGN KEY (`uploaded_by_id`) REFERENCES `auth_user` (`id`),
  CONSTRAINT `booking_file_verified_by_id_3e5fe9ef_fk_auth_user_id` FOREIGN KEY (`verified_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

--
-- Create model BookingHistory
--
CREATE TABLE `booking_history` (
  `id` int NOT NULL AUTO_INCREMENT,
  `previous_status` varchar(20) NOT NULL,
  `new_status` varchar(20) NOT NULL,
  `timestamp` datetime NOT NULL,
  `comment` text NOT NULL,
  `handled_by_role` varchar(50) NOT NULL,
  `booking_id` bigint NOT NULL,
  `changed_by_id` bigint DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `booking_history_booking_id_517fef05` (`booking_id`),
  KEY `booking_history_changed_by_id_5efc11ee` (`changed_by_id`),
  CONSTRAINT `booking_history_booking_id_517fef05_fk_booking_id` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`),
  CONSTRAINT `booking_history_changed_by_id_5efc11ee_fk_auth_user_id` FOREIGN KEY (`changed_by_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB;

--
-- Create model EventDetail
--
CREATE TABLE `booking_event_detail` (
  `id` int NOT NULL AUTO_INCREMENT,
  `event_type` varchar(100) NOT NULL,
  `purpose` text NOT NULL,
  `equipment_needed` text NOT NULL,
  `special_requests` text NOT NULL,
  `setup_time` datetime DEFAULT NULL,
  `teardown_time` datetime DEFAULT NULL,
  `budget` decimal(10,2) DEFAULT NULL,
  `organizer_name` varchar(255) NOT NULL,
  `organizer_contact` varchar(100) NOT NULL,
  `event_schedule` text NOT NULL,
  `booking_id` bigint NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `booking_id` (`booking_id`),
  CONSTRAINT `booking_event_detail_booking_id_8c3c4b1c_fk_booking_id` FOREIGN KEY (`booking_id`) REFERENCES `booking` (`id`)
) ENGINE=InnoDB;

COMMIT;