include apt
require ptero::params

# --- External Services ---
class {'postgresql::server': }
package {'python-psycopg2':
  ensure => present,
}

class {'nginx': }

class {'redis':
  redis_bind_address => '127.0.0.1',
  redis_password     => 'never-enter',
  redis_max_memory   => '0mb',
  version            => '2.8.15',
}

class {'rabbitmq':
  delete_guest_user => true,
  service_manage    => false,
}
package {'python-librabbitmq':
  ensure => present,
}


# --- Auth ---
postgresql::server::db {$ptero::params::auth::database_name :
  user     => $ptero::params::auth::database_username,
  password => $ptero::params::auth::database_password,
}
class {'ptero::auth::web':
  require => Postgresql::Server::Db[$ptero::params::auth::database_name],
}


# --- Shell command ---
class {'ptero::shell_command::rabbitmq': }
class {'ptero::shell_command::redis': }
class {'ptero::shell_command::web':
  require => [
    Class['ptero::shell_command::rabbitmq'],
    Class['ptero::shell_command::redis'],
  ],
}
class {'ptero::shell_command::celery':
  require => [
    Class['ptero::shell_command::rabbitmq'],
    Class['ptero::shell_command::redis'],
  ],
}


# --- Petri ---
postgresql::server::db {$ptero::params::petri::database_name :
  user     => $ptero::params::petri::database_username,
  password => $ptero::params::petri::database_password,
}
class {'ptero::petri::rabbitmq': }
class {'ptero::petri::redis': }
class {'ptero::petri::web':
  require => [
    Class['ptero::petri::rabbitmq'],
    Class['ptero::petri::redis'],
  ],
}
class {'ptero::petri::orchestrator':
  require => [
    Class['ptero::petri::rabbitmq'],
    Class['ptero::petri::redis'],
  ],
}


# --- Workflow ---
postgresql::server::db {$ptero::params::workflow::database_name :
  user     => $ptero::params::workflow::database_username,
  password => $ptero::params::workflow::database_password,
}
class {'ptero::workflow::web':
  require => Postgresql::Server::Db[$ptero::params::workflow::database_name],
}
