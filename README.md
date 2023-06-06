# MDP solver for Pacman<br>
<br>
1)&nbsp;프로젝트 목표 <br>
&nbsp;&nbsp;&nbsp;&nbsp;UC 버클리의 인공지능 예제인 팩맨 프로젝트를 기반으로<br>
&nbsp;&nbsp;&nbsp;&nbsp;Pacman의 환경을 이해하고<br>
&nbsp;&nbsp;&nbsp;&nbsp;K-Scrum 개발 프로세스를 적용하여<br>
&nbsp;&nbsp;&nbsp;&nbsp;다양한 강화학습 알고리즘으로 Pacman을 학습시켜<br>
&nbsp;&nbsp;&nbsp;&nbsp;가장 좋은 성능을 내는 프로젝트입니다.<br>
<br>
2) 게임 규칙
  Pacman Game<br>
  • 팩맨(Pacman)은 맵에 존재하는 모든 음식(Food)를 먹으면 승리한다.<br>
  • 팩맨은 유령(Ghost)에게 닿으면 게임에서 패배한다.<br>
  • 팩맨이 캡슐(Capsule)을 먹으면 맵에 존재하는 유령는 겁먹으며(scared), 겁먹은 유령은 팩맨이 잡을 수 있다.<br>
 <br>
3) 게임 점수<br>
  • 시간이 1 지나면 -1점<br>
  • 음식를 먹으면 +10점<br>
  • 겁먹은 유령을 잡으면 +200점<br>
  • 승리하면 +500점<br>
  • 패배하면 -500점<br>
   <br>
4) 추진 전략 <br>
  • 개발 프로세스 :  K-scrum <br>
  • 협업 툴 : Github, Notion <br>
   <br>
5) 참여인원 <br>
  • 나지영 <br>
  • 이채은 <br>
  • 전정민 <br>
  • 박정원 <br>
   <br>
6) 알고리즘 우선순위 <br>
  • 유령이 근처에 위치할 경우, 유령을 회피한다. <br>
  • 맵 상에 겁먹은 유령이 존재할 경우, 겁먹은 유령을 우선적으로 추적한다. <br>
  • 맵 상에 겁먹은 유령이 없고 캡슐이 존재할 경우, 캡슐을 우선적으로 추적한다. <br>
  • 맵 상에 겁먹은 유령과 캡슐이 모두 없을 경우, 남은 음식을 모두 먹는다. <br>
   <br>
7) 실행방법 <br>
터미널창에서 수행 > pacman-mdp-solver 파일로 내려가 python2 pacman.py -p MDPAgent 명령어 입력
