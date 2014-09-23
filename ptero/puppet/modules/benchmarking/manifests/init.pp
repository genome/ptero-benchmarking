class benchmarking() {
    package {'jq':
        ensure => present,
    }

    file {'/usr/local/bin/benchmark_sleep':
        ensure  => present,
        owner   => root,
        group   => root,
        mode    => '0555',
        source  => 'puppet:///modules/benchmarking/benchmark_sleep',
    }
}
