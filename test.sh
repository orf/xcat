#!/usr/bin/env bats

TEST_URL=${TEST_URL:-http://127.0.0.1:4567/}
FIRST_LINE="<root first=\"1\" second=\"2\" third=\"\">"
OOB_HOST=${OOB_HOST:-localhost:8000}
unset PYTHONWARNINGS

@test "Help: works" {
  run poetry run xcat -- --help
  [ "$status" -eq 0 ]
}

@test "Detect IP: works" {
  run poetry run xcat -- ip
  [ "$status" -eq 0 ]
}

@test "Injections: works" {
  run poetry run xcat -- injections
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "Supports 10 injections:") -ne "0" ]
}

@test "Features: xversion 1 works" {
  run poetry run xcat -- detect "${TEST_URL}" query xversion=1.0 query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
}

@test "Features: xversion 2 works" {
  run poetry run xcat -- detect "${TEST_URL}" query xversion=2.0 query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
}

@test "Features: xversion 3 works" {
  run poetry run xcat -- detect "${TEST_URL}" query xversion=3.0 query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
}


@test "Features: OOB" {
  run poetry run xcat -- detect "${TEST_URL}" query xversion=3.0 query=Rogue --true-string=Lawyer --oob=${OOB_HOST}
  [ "$status" -eq 0 ]
  [ $(echo ${output} | grep -c "oob-http: True") -eq "1" ]
}

@test "Run: Simple" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: without normalization" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --disable=normalize-space
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: Without codepoint search" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --disable=codepoint-search
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: Without codepoint and normalize" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --disable=codepoint-search,normalize-space
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: With OOB server" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --oob=${OOB_HOST}
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: Headers file" {
  cat <<EOF > $BATS_TMPDIR/headers
Cookie: abcdef
SomeHeader: abc
EOF
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --headers=$BATS_TMPDIR/headers
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: Headers file - Invalid" {
  cat <<EOF > $BATS_TMPDIR/headers
Cookie abcdef
EOF
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --headers=$BATS_TMPDIR/headers
  [ "$(echo \"${output}\" | grep -c "Not a valid header line")" -ne "0" ]
}

@test "Run: POST" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer -m POST -e form
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
}

@test "Run: Fast mode" {
  run poetry run xcat -- run "${TEST_URL}" query query=Rogue --true-string=Lawyer --fast
  [ "$status" -eq 0 ]
  [ $(echo "${output}" | grep -c "${FIRST_LINE}") -ne "0" ]
  [ $(echo "${output}" | grep -c "more characters)") -ne "0" ]
}
