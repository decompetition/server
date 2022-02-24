#! /bin/bash

set -e
cd "$(dirname "$0")"

check_env() {
  file="$inf/vars/$1/config.json"
  if [ ! -f "$file" ]; then
    echo "Missing config file $file; run init?" 1>&2
    exit 1
  fi
}

run_ansible() {
  env="$1"
  task="$2"
  shift 2

  check_env "$env"
  ansible-playbook \
    --inventory "$inf/vars/$env/inventory.ini" \
    --extra-vars="envname=$env" \
    --extra-vars="@inf/vars/$env/config.json" \
    "$inf/ansible/$task.yml" \
    "$@"
}

run_delete() {
  tfs="$inf/vars/$1/state.tfstate"
  if [ -f "$tfs" ] && [ $(wc -c < "$tfs") -ge 200 ]; then
    echo "Terraform state is not cleaned up; run teardown first." 1>&2
    exit 1
  fi

  rm -r "$inf/vars/$1"
}

run_init() {
  env="$1"
  shift 1

  if [ -d "$inf/vars/$env" ]; then
    echo "Environment $env already exists." 1>&2
    exit 1
  fi

  mkdir -p "$inf/vars/$env"
  cat <<EOF > "$inf/vars/$env/config.json"
{
  "aws_region":        "us-west-1",
  "aws_instance":      "t3.micro",
  "aws_access_key":    "YOUR AWS ACCESS KEY",
  "aws_secret_key":    "YOUR AWS SECRET KEY",
  "aws_keypair":       "YOUR AWS KEYPAIR NAME",

  "sql_database":      "decompetition",
  "sql_username":      "deco",
  "sql_password":      "$(head -c  27 /dev/urandom | base64 | tr +/ xl)",

  "app_servers":       2,
  "app_secret":        "$(head -c 108 /dev/urandom | base64 | tr +/ xl)",
  "app_start_time":    "YYYY-MM-DD HH:MM",
  "app_end_time":      "YYYY-MM-DD HH:MM",

  "challenge_dir":     "/ABSOLUTE/PATH/TO/CHALLENGE/DIR",
  "containers": [
    "decompetition/builder-2021"
  ]
}
EOF

  echo "Config file created at inf/vars/$env/config.json"
  echo "Edit this file and add your secrets!"
}

run_ssh() {
  env="$1"
  shift 1

  ssh -F "$inf/vars/$env/ssh_config" "$@"
}

run_terraform() {
  if [ ! -d "$inf/terraform/.terraform" ]; then
    echo "Initializing Terraform..."
    terraform -chdir="$inf/terraform" init
  fi

  env="$1"
  task="$2"
  shift 2

  check_env "$env"
  terraform -chdir="$inf/terraform" "$task" \
    -state="$inf/vars/$env/state.tfstate" \
    -var-file="$inf/vars/$env/config.json" \
    -var="envname=$env" \
    "$@"
}

usage() {
  cat <<EOF 1>&2
USAGE: $0 task env [extra-args]

Available tasks (S=shell; T=terraform; A=ansible):
  init       S  Create config files for a new environment.
  provision  T  Create or update the AWS infrastructure.
  configure  A  Configure the AWS machines and deploy the challenges and server.

  update     A  Update all APT packages.
  prune      A  Clean up unused Docker images.
  growfs     A  Resize the root filesystem.
  ssh        S  Connect to a host via SSH.

  teardown   T  Delete the AWS infrastructure.
  delete     S  Delete the config files.
EOF
}

if [ $# -lt 2 ]; then
  usage
  exit 1
fi

task="$1"
env="$2"
inf="$(cd "$(dirname "$0")"; pwd)/inf"
shift 2

if echo "$env" | grep -qE '^[[:alnum:]]+$'; then
  : All good, nothing to do.
else
  echo "Invalid environment name: $env" 1>&2
  echo "Environment names must be alphanumeric." 1>&2
  exit 1
fi

case "$task" in
  init)      run_init      "$env" ;;
  delete)    run_delete    "$env" ;;
  ssh)       run_ssh       "$env" "$@" ;;

  provision) run_terraform "$env" apply   "$@" ;;
  teardown)  run_terraform "$env" destroy "$@" ;;

  configure) run_ansible   "$env" "$task" "$@" ;;
  growfs)    run_ansible   "$env" "$task" "$@" ;;
  redeploy)  run_ansible   "$env" "$task" "$@" ;;
  update)    run_ansible   "$env" "$task" "$@" ;;

  *)
    usage
    exit 1
    ;;
esac
