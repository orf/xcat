#!/usr/bin/env bats

TEST_URL=${TEST_URL:-http://localhost:4567/}
FIRST_LINE="<root first=\"1\" second=\"2\" third=\"\">"
unset PYTHONWARNINGS

@test "Help works" {
  run xcat --help
  [ "$status" -eq 0 ]
}

@test "Detect IP works" {
  run xcat ip
  [ "$status" -eq 0 ]
}

@test "Features: xversion 1 works" {
  run xcat detect ${TEST_URL} query xversion=1.0 query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
}

@test "Features: xversion 2 works" {
  run xcat detect ${TEST_URL} query xversion=2.0 query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
}

@test "Features: xversion 3 works" {
  run xcat detect ${TEST_URL} query xversion=3.0 query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
}


@test "Features: OOB" {
  run xcat detect ${TEST_URL} query xversion=3.0 query=Rogue --true-string=Lawyer --oob=localhost:8000
  [ "$status" -eq 0 ]
  [ $(echo ${output} | grep -c "oob-http: True") -eq "1" ]
}

@test "Run: Simple" {
  run xcat run ${TEST_URL} query query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "${FIRST_LINE}" ]
}

@test "Run: without normalization" {
  run xcat run ${TEST_URL} query query=Rogue --true-string=Lawyer --disable=normalize-space
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "${FIRST_LINE}" ]
}

@test "Run: Without codepoint search" {
  run xcat run ${TEST_URL} query query=Rogue --true-string=Lawyer --disable=codepoint-search
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "${FIRST_LINE}" ]
}

@test "Run: Without codepoint and normalize" {
  run xcat run ${TEST_URL} query query=Rogue --true-string=Lawyer --disable=codepoint-search,normalize-space
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "${FIRST_LINE}" ]
}

@test "Run: With OOB server" {
  run xcat run ${TEST_URL} query query=Rogue --true-string=Lawyer --oob=localhost:8000
  [ "$status" -eq 0 ]
  [ "${lines[0]}" = "${FIRST_LINE}" ]
}
