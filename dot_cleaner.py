import os
import time

def remove_dot_underscore_files(directory):
    # directory 안의 파일과 폴더를 재귀적으로 탐색
    for root, dirs, files in os.walk(directory):
        for file in files:
            # 파일이 '._'로 시작하는지 확인
            if file.startswith("._"):
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"파일 삭제됨: {file_path}")
                except Exception as e:
                    print(f"파일 삭제 실패: {file_path} - {e}")

# 현재 디렉터리에서 실행
current_directory = os.getcwd()
i = 0

while True:
    remove_dot_underscore_files(current_directory)
    i += 1
    print(f"제거 완료! ({i}번째)")
    time.sleep(1)