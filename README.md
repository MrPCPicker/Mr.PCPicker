# Mr.PCPicker


### 기본 설정 

- 브랜치 `master`, `dev` 두 개 만들기 (master는 최종 배포용, dev는 개발용)
- Repository > Settings > General > Default branch > `dev`로 설정


### 개발 순서

- Repository > Project > `버전 이름`으로 생성
- Repository > Issue > `기능 이름`으로 생성
    - Assignees : 나로 설정
    - Projects : 방금 생성한 프로젝트로 설정

<br>

- VSCode > `git pull`
- VSCode > `git branch 이름`로 로컬 브랜치 생성 (Issue 이름 사용)
- VSCode > `git switch 이름`으로 브랜치 이동 (Issue 이름 사용)
- VSCode > 코드 작업
- VSCode > `git add .` 로 올리기
- VSCode > `git commit -m '메세지'` 로 커밋 (깃모지 사용 추천)

<br>

[코드를 올리는 입장]
- Repository > `Compare & pull request` 버튼
    - Description : 굉장히 자세하게 적기
    - Reviewer : 내 코드를 보고 피드백을 줄 사람, Merge 는 내가 한다
    - Project : 프로젝트 선택한 후에, Description에 `closes #이슈번호`를 작성하면, 자동으로 Done 으로 이동한다

[코드를 리뷰하는 입장]
- Repository > Pull Request > Files Changed > 코멘트 남겨 리뷰하기
    - Finish your review > Approve : 코드를 잘 짰을때
    - Finish your review > Request changes : 코드를 잘 못 짰을때

[코드를 올리는 입장]
- Repository > Pull Request > Conform merge : `dev`에 병합하기
- Repository > Pull Request > Delete Branch : 병합된 브랜치는 삭제하기

<br>

- VSCode > `git switch dev`로 이동
- VSCode > `git pull` 로 dev 브랜치 패치 받기
- VSCode > `git branch -D 이름` 으로 원격에서 병합된 후의 로컬 브랜치 삭제하기

--- 

### git 명령어

- origin/HEAD : 내가 현재 있는 위치

<br>

- `git branch` : 브랜치 목록 확인
- `git branch -r` : 원격 브랜치 목록 확인
- `git branch -a` : 로컬 브랜치 목록 확인

<br>

- `git branch 이름` : (로컬에) 새 브랜치 생성
- `git push --set-upstream origin 이름 ` : (원격에) 브랜치 올리기

```
브랜치로 사용할 수 있는 이름

#1_test : 불가
1#_test : 가능
1_test : 가능
test#1 : 가능
```

<br>

- `git branch -d 이름` : 병합된 브랜치 삭제
- `git branch -D 이름` : 브랜치 강제 삭제
- `git push origin --delete 이름` : 원격 브랜치 삭제

<br>

- `git switch 이름` : 다른 브랜치로 전환
- `git switch -c 이름` : 새 브랜치 생성 후 전환
- `git switch -c 이름 코드` : 특정 커밋에서 새 브랜치 생성 후 전환

<br>





