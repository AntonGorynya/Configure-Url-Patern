#!/usr/bin/perl -w

use strict;
use XML::Simple;

#кажется есть проблемы с кодировкой+добавил ковычки
use utf8;
binmode(STDOUT,':utf8');

my $xml = new XML::Simple;
my $data = $xml->XMLin("/home/dieul/Документы/Selectel/download\ bad\ sites/dump.xml");


open (ABUSE_IP, ">/home/dieul/Документы/Selectel/download\ bad\ sites/ip-abuse.txt");

foreach my $key (keys (%{$data-> {content}})) {
    foreach my $key2 (keys (%{$data->{content}->{$key}})) {
        if ($key2 eq 'ip') {
            if (ref $data->{content}->{$key}->{ip} eq 'ARRAY') {
                foreach my $ip (@{$data->{content}->{$key}->{ip}}) {
                    print ABUSE_IP "$ip\n";
                };
            } else {
                print ABUSE_IP "$data->{content}->{$key}->{ip}\n";
            };
        };
    };
};
close ABUSE_IP;

open (ABUSE_URL, ">/home/dieul/Документы/Selectel/download\ bad\ sites/url-abuse2.txt");

foreach my $key (keys (%{$data-> {content}})) {
    foreach my $key2 (keys (%{$data->{content}->{$key}})) {
        if ($key2 eq 'url') {
            if (ref $data->{content}->{$key}->{url} eq 'ARRAY') {
                foreach my $url (@{$data->{content}->{$key}->{url}}) {
                    print ABUSE_URL "$url\n";
                };
            } else {
                print ABUSE_URL "$data->{content}->{$key}->{url}\n";
            };
        };
    };
};
close ABUSE_URL;
