#!/bin/bash

# 檢查參數
if [ "$#" -ne 2 ]; then
  echo "Usage: $0 <project_name> <env>"
  exit 1
fi

project_name=$1
env=$2
backup_dir=./report/backup
source_dir=./web/report/$project_name/$env
check_dir=./report/$project_name/$env
date_str=$(date +%Y%m%d)
backup_file="${project_name}_${env}_${date_str}.zip"

# 檢查資料夾是否存在且不為空
if [ ! -d "$check_dir" ] || [ -z "$(ls -A $check_dir)" ]; then
  echo "Error: Directory $check_dir not found or is empty."
  exit 1
fi

# 壓縮資料夾
zip -r "$backup_file" "$source_dir" > /dev/null 2>&1
if [ "$?" -ne 0 ]; then
  echo "Error: Failed to create backup."
  exit 1
fi

# 確保備份目錄存在
mkdir -p "$backup_dir"

# 移動壓縮檔案到備份資料夾
mv "$backup_file" "$backup_dir"
if [ "$?" -ne 0 ]; then
  echo "Error: Failed to move backup to $backup_dir."
  exit 1
fi

# 刪除原資料夾
rm -rf "$check_dir"
if [ "$?" -ne 0 ]; then
  echo "Error: Failed to delete original directory."
  exit 1
fi

# 重新建立資料夾結構
mkdir -p "$check_dir/html" "$check_dir/json/history" "$check_dir/log"
touch "$check_dir/html/.gitkeep" "$check_dir/json/.gitkeep" "$check_dir/json/history/.gitkeep" "$check_dir/log/.gitkeep"

# 確認資料夾結構是否正確
if [ ! -d "$check_dir/html" ] || [ ! -d "$check_dir/json/history" ] || [ ! -d "$check_dir/log" ] || \
   [ ! -f "$check_dir/html/.gitkeep" ] || [ ! -f "$check_dir/json/.gitkeep" ] || [ ! -f "$check_dir/json/history/.gitkeep" ] || [ ! -f "$check_dir/log/.gitkeep" ]; then
  echo "Error: Failed to recreate directory structure."
  exit 1
fi

echo "Backup and cleanup completed successfully."