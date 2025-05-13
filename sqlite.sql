--
-- Create model Venue
--
CREATE TABLE `venue` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `name` varchar(100) NOT NULL, `description` text NULL, `capacity` integer NOT NULL, `location` varchar(200) NOT NULL, `category` varchar(50) NULL, `handled_by` varchar NOT NULL, `is_available` tinyint(1) NOT NULL, `requires_approval` tinyint(1) NOT NULL, `requires_payment` tinyint(1) NOT NULL, `requires_documents` tinyint(1) NOT NULL, `features` text NOT NULL CHECK ((JSON_VALID(`features`) OR `features` IS NULL)));
--
-- Create model VenueAvailability
--
CREATE TABLE `venue_availability` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `date` date NOT NULL, `start_time` time NOT NULL, `end_time` time NOT NULL, `is_available` tinyint(1) NOT NULL, `venue_id` bigint NOT NULL REFERENCES `venue` (`id`) DEFERRABLE INITIALLY DEFERRED);
CREATE UNIQUE INDEX `venue_availability_venue_id_date_start_time_end_time_dc38011e_uniq` ON `venue_availability` (`venue_id`, `date`, `start_time`, `end_time`);
CREATE INDEX `venue_availability_venue_id_89d52640` ON `venue_availability` (`venue_id`);

--
-- Create model UserProfile
--
CREATE TABLE `user_profile` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `profile_picture` varchar(100) NOT NULL, `bio` text NULL, `date_of_birth` date NULL, `gender` varchar(10) NULL, `location` varchar(100) NULL);
--
-- Create model User
--
CREATE TABLE `auth_user` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `password` varchar(128) NOT NULL, `last_login` datetime NULL, `is_superuser` tinyint(1) NOT NULL, `is_staff` tinyint(1) NOT NULL, `is_active` tinyint(1) NOT NULL, `date_joined` datetime NOT NULL, `email` varchar(254) NOT NULL UNIQUE, `first_name` varchar(100) NOT NULL, `last_name` varchar(100) NOT NULL, `user_type` varchar(20) NOT NULL, `student_id` varchar(20) NULL, `phone_number` varchar(20) NOT NULL);
CREATE TABLE `auth_user_groups` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `user_id` bigint NOT NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED, `group_id` integer NOT NULL REFERENCES `auth_group` (`id`) DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE `auth_user_user_permissions` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `user_id` bigint NOT NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED, `permission_id` integer NOT NULL REFERENCES `auth_permission` (`id`) DEFERRABLE INITIALLY DEFERRED);
--
-- Create model AdminProfile
--
CREATE TABLE `admin_profile` (`userprofile_ptr_id` bigint NOT NULL PRIMARY KEY REFERENCES `user_profile` (`id`) DEFERRABLE INITIALLY DEFERRED, `admin_id` varchar(20) NULL);
--
-- Create model StaffProfile
--
CREATE TABLE `staff_profile` (`userprofile_ptr_id` bigint NOT NULL PRIMARY KEY REFERENCES `user_profile` (`id`) DEFERRABLE INITIALLY DEFERRED, `staff_id` varchar(20) NULL, `department` varchar(100) NULL, `position` varchar(100) NULL);
--
-- Create model StudentProfile
--
CREATE TABLE `student_profile` (`userprofile_ptr_id` bigint NOT NULL PRIMARY KEY REFERENCES `user_profile` (`id`) DEFERRABLE INITIALLY DEFERRED, `student_id` varchar(20) NULL, `major` varchar(100) NULL, `organization` varchar(100) NULL, `year` integer NOT NULL);
--
-- Add field user to userprofile
--
CREATE TABLE `new__user_profile` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `profile_picture` varchar(100) NOT NULL, `bio` text NULL, `date_of_birth` date NULL, `gender` varchar(10) NULL, `location` varchar(100) NULL, `user_id` bigint NOT NULL UNIQUE REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED);
INSERT INTO `new__user_profile` (`id`, `profile_picture`, `bio`, `date_of_birth`, `gender`, `location`, `user_id`) SELECT `id`, `profile_picture`, `bio`, `date_of_birth`, `gender`, `location`, NULL FROM `user_profile`;
DROP TABLE `user_profile`;
ALTER TABLE `new__user_profile` RENAME TO `user_profile`;
CREATE UNIQUE INDEX `auth_user_groups_user_id_group_id_94350c0c_uniq` ON `auth_user_groups` (`user_id`, `group_id`);
CREATE INDEX `auth_user_groups_user_id_6a12ed8b` ON `auth_user_groups` (`user_id`);
CREATE INDEX `auth_user_groups_group_id_97559544` ON `auth_user_groups` (`group_id`);
CREATE UNIQUE INDEX `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` ON `auth_user_user_permissions` (`user_id`, `permission_id`);
CREATE INDEX `auth_user_user_permissions_user_id_a95ead1b` ON `auth_user_user_permissions` (`user_id`);
CREATE INDEX `auth_user_user_permissions_permission_id_1fbb5f2c` ON `auth_user_user_permissions` (`permission_id`);

--
-- Create model Booking
--
CREATE TABLE `booking` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `booking_code` varchar(20) NOT NULL UNIQUE, `title` varchar(255) NOT NULL, `description` text NOT NULL, `start_time` datetime NOT NULL, `end_time` datetime NOT NULL, `attendees_count` integer unsigned NOT NULL CHECK (`attendees_count` >= 0), `status` varchar(20) NOT NULL, `created_at` datetime NOT NULL, `updated_at` datetime NOT NULL, `payment_required` tinyint(1) NOT NULL, `payment_amount` decimal NULL, `payment_completed` tinyint(1) NOT NULL, `payment_reference` varchar(100) NOT NULL, `requires_approval` tinyint(1) NOT NULL, `approval_date` datetime NULL, `documents_required` tinyint(1) NOT NULL, `documents_verified` tinyint(1) NOT NULL, `approved_by_id` bigint NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED, `user_id` bigint NOT NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED, `venue_id` bigint NOT NULL REFERENCES `venue` (`id`) DEFERRABLE INITIALLY DEFERRED);
--
-- Create model BookingFeedback
--
CREATE TABLE `booking_feedback` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `content` text NOT NULL, `is_internal` tinyint(1) NOT NULL, `feedback_type` varchar(50) NOT NULL, `created_at` datetime NOT NULL, `booking_id` bigint NOT NULL REFERENCES `booking` (`id`) DEFERRABLE INITIALLY DEFERRED, `staff_id` bigint NOT NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED);
--
-- Create model BookingFile
--
CREATE TABLE `booking_file` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `file` varchar(100) NOT NULL, `file_name` varchar(255) NOT NULL, `file_type` varchar(50) NOT NULL, `document_type` varchar(100) NOT NULL, `description` text NOT NULL, `uploaded_at` datetime NOT NULL, `is_verified` tinyint(1) NOT NULL, `verified_at` datetime NULL, `booking_id` bigint NOT NULL REFERENCES `booking` (`id`) DEFERRABLE INITIALLY DEFERRED, `uploaded_by_id` bigint NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED, `verified_by_id` bigint NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED);
--
-- Create model BookingHistory
--
CREATE TABLE `booking_history` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `previous_status` varchar(20) NOT NULL, `new_status` varchar(20) NOT NULL, `timestamp` datetime NOT NULL, `comment` text NOT NULL, `handled_by_role` varchar(50) NOT NULL, `booking_id` bigint NOT NULL REFERENCES `booking` (`id`) DEFERRABLE INITIALLY DEFERRED, `changed_by_id` bigint NULL REFERENCES `auth_user` (`id`) DEFERRABLE INITIALLY DEFERRED);
--
-- Create model EventDetail
--
CREATE TABLE `booking_event_detail` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `event_type` varchar(100) NOT NULL, `purpose` text NOT NULL, `equipment_needed` text NOT NULL, `special_requests` text NOT NULL, `setup_time` datetime NULL, `teardown_time` datetime NULL, `budget` decimal NULL, `organizer_name` varchar(255) NOT NULL, `organizer_contact` varchar(100) NOT NULL, `event_schedule` text NOT NULL, `booking_id` bigint NOT NULL UNIQUE REFERENCES `booking` (`id`) DEFERRABLE INITIALLY DEFERRED);
--
-- Create index booking_status_b99f68_idx on field(s) status of model booking
--
CREATE INDEX `booking_status_b99f68_idx` ON `booking` (`status`);
--
-- Create index booking_user_id_acf7f7_idx on field(s) user of model booking
--
CREATE INDEX `booking_user_id_acf7f7_idx` ON `booking` (`user_id`);
--
-- Create index booking_venue_i_1ab500_idx on field(s) venue of model booking
--
CREATE INDEX `booking_venue_i_1ab500_idx` ON `booking` (`venue_id`);
--
-- Create index booking_start_t_616860_idx on field(s) start_time, end_time of model booking
--
CREATE INDEX `booking_start_t_616860_idx` ON `booking` (`start_time`, `end_time`);
CREATE INDEX `booking_approved_by_id_30bf1330` ON `booking` (`approved_by_id`);
CREATE INDEX `booking_user_id_1bd7cb6e` ON `booking` (`user_id`);
CREATE INDEX `booking_venue_id_204dff63` ON `booking` (`venue_id`);
CREATE INDEX `booking_feedback_booking_id_5b8eba55` ON `booking_feedback` (`booking_id`);
CREATE INDEX `booking_feedback_staff_id_6d3fc320` ON `booking_feedback` (`staff_id`);
CREATE INDEX `booking_file_booking_id_fad8c254` ON `booking_file` (`booking_id`);
CREATE INDEX `booking_file_uploaded_by_id_c058674d` ON `booking_file` (`uploaded_by_id`);
CREATE INDEX `booking_file_verified_by_id_3e5fe9ef` ON `booking_file` (`verified_by_id`);
CREATE INDEX `booking_history_booking_id_517fef05` ON `booking_history` (`booking_id`);
CREATE INDEX `booking_history_changed_by_id_5efc11ee` ON `booking_history` (`changed_by_id`);

--
-- Create model EmailLog
--
CREATE TABLE `email_log` (`id` integer NOT NULL PRIMARY KEY AUTO_INCREMENT, `recipient_email` varchar(254) NOT NULL, `subject` varchar(200) NOT NULL, `message` text NOT NULL, `sent_at` datetime NOT NULL, `status` varchar(20) NOT NULL);

