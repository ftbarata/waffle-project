CREATE TABLE IF NOT EXISTS plugin_admin_command_interface_state (
id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
cellnumber BIGINT UNSIGNED,
state VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_bin,
PRIMARY KEY(id)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET utf8
DEFAULT COLLATE utf8_general_ci;


CREATE TABLE IF NOT EXISTS plugin_admin_command_interface_operation_list (
id INTEGER UNSIGNED NOT NULL AUTO_INCREMENT,
menu_option INTEGER UNSIGNED,
codename VARCHAR(50) CHARACTER SET utf8 COLLATE utf8_bin,
operation VARCHAR(500) CHARACTER SET utf8 COLLATE utf8_bin,
PRIMARY KEY(id)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET utf8
DEFAULT COLLATE utf8_general_ci;