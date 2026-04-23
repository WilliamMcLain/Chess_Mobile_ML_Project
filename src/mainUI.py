"""
mainUI.py — Flask UI. Uses main_play.moveInput() for human turns,
computer.Computer.move() for computer turns. Writes to score.xlsx via computer.py.
"""

import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import main_play, csv_setup
from computer import Computer
from computer import score_print_summary

app  = Flask(__name__)
CORS(app)

# Global computer instance — created when human picks a side
_computer: Computer = None
_all_moves: list    = []   # full game move log (both sides) for score.xlsx

HTML = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Chess</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Courier New', monospace; background: #111; color: #ddd;
       display: flex; flex-direction: column; align-items: center; padding: 24px 16px; min-height: 100vh; }
h1 { font-size: 18px; letter-spacing: .2em; color: #aaa; margin-bottom: 20px; text-transform: uppercase; }
#app { display: flex; gap: 28px; flex-wrap: wrap; justify-content: center; width: 100%; max-width: 860px; }
#board-wrap { display: flex; flex-direction: column; align-items: center; gap: 4px; }
#board-row  { display: flex; align-items: flex-start; }
.rank-col   { display: flex; flex-direction: column; width: 20px; }
.rank-col span { height: 62px; line-height: 62px; font-size: 11px; color: #555; text-align: right; padding-right: 4px; }
#board { display: grid; grid-template-columns: repeat(8, 62px); grid-template-rows: repeat(8, 62px); border: 2px solid #333; }
.file-row { display: flex; padding-left: 20px; }
.file-row span { width: 62px; text-align: center; font-size: 11px; color: #555; padding-top: 3px; }
.sq { width:62px; height:62px; display:flex; align-items:center; justify-content:center;
      font-size:38px; cursor:pointer; position:relative; user-select:none; transition:filter .1s; }
.sq.light { background:#c8a97e; } .sq.dark { background:#7a5230; }
.sq:hover { filter:brightness(1.15); }
.sq.selected { background:#e8e84a !important; }
.sq.valid-move::after { content:''; position:absolute; width:20px; height:20px; border-radius:50%;
                         background:rgba(0,0,0,0.3); pointer-events:none; }
.sq.valid-capture { outline:3px solid rgba(220,50,50,.75); outline-offset:-3px; }
#panel { display:flex; flex-direction:column; gap:12px; min-width:220px; flex:1; max-width:280px; }
.card { background:#1c1c1c; border:1px solid #2a2a2a; border-radius:8px; padding:12px 14px; }
.card-title { font-size:10px; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color:#555; margin-bottom:8px; }
#side-pick { display:flex; gap:8px; }
.side-btn { flex:1; padding:10px 0; border:1px solid #333; border-radius:6px; background:#222; color:#aaa;
            font-family:inherit; font-size:13px; cursor:pointer; transition:background .15s,color .15s; }
.side-btn:hover { background:#2a2a2a; color:#eee; }
.side-btn.active { background:#3a3a3a; color:#fff; border-color:#666; }
#input-form { display:flex; flex-direction:column; gap:8px; }
.input-row  { display:flex; flex-direction:column; gap:3px; }
.input-label { font-size:10px; color:#555; letter-spacing:.08em; text-transform:uppercase; }
.input-field { background:#151515; border:1px solid #2a2a2a; border-radius:5px; color:#ddd;
               font-family:inherit; font-size:14px; padding:7px 10px; width:100%; outline:none; }
.input-field:focus { border-color:#555; }
#submit-btn { padding:9px; border:1px solid #444; border-radius:6px; background:#282828; color:#eee;
              font-family:inherit; font-size:13px; cursor:pointer; margin-top:2px; }
#submit-btn:hover { background:#333; } #submit-btn:disabled { opacity:.4; cursor:default; }
#status-text { font-size:13px; color:#ccc; }
#error-text  { font-size:12px; color:#c05050; min-height:16px; margin-top:4px; }
#turn-row    { display:flex; align-items:center; gap:8px; font-size:13px; }
#turn-dot    { width:11px; height:11px; border-radius:50%; flex-shrink:0; }
#log { max-height:180px; overflow-y:auto; display:flex; flex-direction:column; gap:2px; }
.log-entry { font-size:11px; color:#666; padding:2px 0; border-bottom:1px solid #222; }
.log-entry:last-child { border:none; }
#score-card { font-size:12px; color:#aaa; line-height:1.7; }
#captured-wrap { display:flex; flex-wrap:wrap; gap:1px; min-height:28px; }
.cap { font-size:20px; }
#reset-btn { padding:9px; border:1px solid #333; border-radius:6px; background:#1c1c1c;
             color:#888; font-family:inherit; font-size:12px; cursor:pointer; }
#reset-btn:hover { color:#ccc; border-color:#555; }
#promo-overlay { display:none; position:fixed; inset:0; background:rgba(0,0,0,.7); z-index:99;
                 align-items:center; justify-content:center; }
#promo-overlay.show { display:flex; }
#promo-box { background:#1c1c1c; border:1px solid #333; border-radius:10px; padding:20px; display:flex; gap:10px; }
.promo-btn { font-size:46px; cursor:pointer; padding:8px; border:1px solid #333; border-radius:6px; background:#222; }
.promo-btn:hover { background:#2e2e2e; }
</style>
</head>
<body>
<h1>Chess</h1>
<div id="app">
  <div id="board-wrap">
    <div id="board-row">
      <div class="rank-col" id="ranks"></div>
      <div id="board"></div>
    </div>
    <div class="file-row" id="files"></div>
  </div>
  <div id="panel">
    <div class="card">
      <div class="card-title">Choose side (b or w)</div>
      <div id="side-pick">
        <button class="side-btn" id="btn-w" onclick="chooseSide('w')">♔ White</button>
        <button class="side-btn" id="btn-b" onclick="chooseSide('b')">♚ Black</button>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Turn</div>
      <div id="turn-row"><span id="turn-dot"></span><span id="turn-text">Pick a side</span></div>
    </div>
    <div class="card">
      <div class="card-title">Make a move</div>
      <div id="input-form">
        <div class="input-row">
          <span class="input-label">start.pos (e.g. a2)</span>
          <input class="input-field" id="inp-start" maxlength="2" placeholder="a2" />
        </div>
        <div class="input-row">
          <span class="input-label">piece (p q b c h k)</span>
          <input class="input-field" id="inp-piece" maxlength="1" placeholder="p" />
        </div>
        <div class="input-row">
          <span class="input-label">end.pos (e.g. a4)</span>
          <input class="input-field" id="inp-end" maxlength="2" placeholder="a4" />
        </div>
        <button id="submit-btn" onclick="submitMove()" disabled>Submit move</button>
        <div id="error-text"></div>
      </div>
    </div>
    <div class="card">
      <div class="card-title">Status</div>
      <div id="status-text">Select a side to begin</div>
    </div>
    <div class="card">
      <div class="card-title">Score</div>
      <div id="score-card">—</div>
    </div>
    <div class="card">
      <div class="card-title">Captured</div>
      <div id="captured-wrap"></div>
    </div>
    <div class="card">
      <div class="card-title">Move log</div>
      <div id="log"><span class="log-entry">No moves yet</span></div>
    </div>
    <button id="reset-btn" onclick="resetGame()">New game</button>
  </div>
</div>
<div id="promo-overlay"><div id="promo-box"></div></div>

<script>
const SYM    = {wk:'♔',wq:'♕',wc:'♖',wb:'♗',wh:'♘',wp:'♙',bk:'♚',bq:'♛',bc:'♜',bb:'♝',bh:'♞',bp:'♟'};
const PNAMES = {p:'Pawn',q:'Queen',k:'King',b:'Bishop',h:'Knight',c:'Rook'};
const VALS   = {p:1,h:3,b:3,c:5,q:9,k:100};

let board, playerSide, currentTurn, captured, waitingForComputer;

function initBoard(){
  return [
    ['bc','bh','bb','bq','bk','bb','bh','bc'],
    ['bp','bp','bp','bp','bp','bp','bp','bp'],
    ['e','e','e','e','e','e','e','e'],['e','e','e','e','e','e','e','e'],
    ['e','e','e','e','e','e','e','e'],['e','e','e','e','e','e','e','e'],
    ['wp','wp','wp','wp','wp','wp','wp','wp'],
    ['wc','wh','wb','wq','wk','wb','wh','wc']
  ];
}

function notation(r,c){ return String.fromCharCode(97+c)+(8-r); }

function resetGame(){
  board=initBoard(); playerSide=null; currentTurn='w'; captured=[];
  waitingForComputer=false;
  document.getElementById('log').innerHTML='<span class="log-entry">No moves yet</span>';
  document.getElementById('captured-wrap').innerHTML='';
  document.getElementById('score-card').textContent='—';
  document.getElementById('submit-btn').disabled=true;
  document.getElementById('turn-text').textContent='Pick a side';
  document.getElementById('turn-dot').style.background='#333';
  ['btn-w','btn-b'].forEach(id=>document.getElementById(id).classList.remove('active'));
  setStatus('Select a side to begin'); setError(''); clearInputs();
  fetch('/reset',{method:'POST'}).catch(()=>{});
  render();
}

function chooseSide(side){
  playerSide=side;
  document.getElementById('btn-w').classList.toggle('active',side==='w');
  document.getElementById('btn-b').classList.toggle('active',side==='b');
  document.getElementById('submit-btn').disabled=false;
  setStatus("Your turn — enter start.pos, piece, end.pos");
  fetch('/start',{method:'POST',headers:{'Content-Type':'application/json'},
    body:JSON.stringify({side})});
  // If human is black, computer (white) goes first
  if(side==='b'){
    currentTurn='w';
    updateTurnDisplay();
    triggerComputerMove();
  } else {
    updateTurnDisplay();
  }
}

async function submitMove(){
  if(waitingForComputer){ setError("Wait for computer to move."); return; }
  const start=document.getElementById('inp-start').value.trim().toLowerCase();
  const piece=document.getElementById('inp-piece').value.trim().toLowerCase();
  const end  =document.getElementById('inp-end').value.trim().toLowerCase();
  if(start.length!==2){ setError('start.pos must be 2 chars e.g. a2'); return; }
  if(piece.length!==1){ setError('piece must be 1 char e.g. p'); return; }
  if(end.length!==2)  { setError('end.pos must be 2 chars e.g. a4'); return; }
  setError('');
  try {
    const res  = await fetch('/move',{method:'POST',headers:{'Content-Type':'application/json'},
                   body:JSON.stringify({side:currentTurn,piece,start,end})});
    const data = await res.json();
    if(data.valid){
      applyMove(start,piece,end);
      if(data.score) updateScoreCard(data.score);
      clearInputs();
      // Trigger computer response
      currentTurn=currentTurn==='w'?'b':'w';
      updateTurnDisplay();
      triggerComputerMove();
    } else {
      setError(data.reason||"sorry, that input wasn't correct");
    }
  } catch(e){ setError('Backend unreachable — is Flask running?'); }
}

async function triggerComputerMove(){
  waitingForComputer=true;
  document.getElementById('submit-btn').disabled=true;
  setStatus("Computer is thinking...");
  await new Promise(r=>setTimeout(r,400));
  try {
    const res  = await fetch('/computer_move',{method:'POST'});
    const data = await res.json();
    if(data.moved){
      applyComputerMove(data.pt, data.start, data.end, data.captured_piece);
      if(data.score) updateScoreCard(data.score);
    } else {
      setStatus(data.reason||"Computer has no moves.");
    }
  } catch(e){ setStatus("Computer move failed — check backend."); }
  waitingForComputer=false;
  currentTurn=playerSide;
  updateTurnDisplay();
  document.getElementById('submit-btn').disabled=false;
  setStatus("Your turn — enter start.pos, piece, end.pos");
  render();
}

function applyMove(start,pieceType,end){
  const sc=start.charCodeAt(0)-97, sr=8-parseInt(start[1]);
  const ec=end.charCodeAt(0)-97,   er=8-parseInt(end[1]);
  const fp=currentTurn+pieceType, target=board[er][ec];
  if(target!=='e'){ captured.push(target); updateCaptured(); }
  board[er][ec]=fp; board[sr][sc]='e';
  addLog(fp,start,end,target);
  const promoRow=currentTurn==='w'?0:7;
  if(pieceType==='p'&&er===promoRow){ showPromo(er,ec,currentTurn); return; }
  render();
}

function applyComputerMove(pt, start, end, capPiece){
  const compSide = playerSide==='w'?'b':'w';
  const sc=start.charCodeAt(0)-97, sr=8-parseInt(start[1]);
  const ec=end.charCodeAt(0)-97,   er=8-parseInt(end[1]);
  const fp=compSide+pt, target=board[er][ec];
  if(target!=='e'){ captured.push(target); updateCaptured(); }
  board[er][ec]=fp; board[sr][sc]='e';
  addLog(fp,start,end,target);
  render();
}

function updateScoreCard(score){
  const el=document.getElementById('score-card');
  el.innerHTML=`You: <b>${score.human}</b> &nbsp; Computer: <b>${score.computer}</b> &nbsp; `+
    `<span style="color:${score.diff>0?'#c05050':score.diff<0?'#50c070':'#aaa'}">`+
    `${score.diff>0?'Computer winning':score.diff<0?'You winning':'Even'} `+
    `(${score.diff>0?'+':''}${score.diff})</span>`;
}

function updateTurnDisplay(){
  const dot=document.getElementById('turn-dot');
  dot.style.background=currentTurn==='w'?'#c8a97e':'#2a2a2a';
  dot.style.border=currentTurn==='w'?'1.5px solid #888':'1.5px solid #aaa';
  document.getElementById('turn-text').textContent=currentTurn==='w'?"White's turn":"Black's turn";
}
function setStatus(m){ document.getElementById('status-text').textContent=m; }
function setError(m)  { document.getElementById('error-text').textContent=m; }
function clearInputs(){ ['inp-start','inp-piece','inp-end'].forEach(id=>document.getElementById(id).value='');
                        document.getElementById('inp-start').focus(); }

function addLog(piece,start,end,cap){
  const log=document.getElementById('log');
  if(log.querySelector('span'))log.innerHTML='';
  const d=document.createElement('div'); d.className='log-entry';
  const side=piece[0]==='w'?'White':'Black';
  d.textContent=`${side}: ${PNAMES[piece[1]]||piece[1]} ${start}→${end}${cap!=='e'?' ✕':''}`;
  log.prepend(d);
}
function updateCaptured(){
  document.getElementById('captured-wrap').innerHTML=captured.map(p=>`<span class="cap">${SYM[p]||p}</span>`).join('');
}
function handleSquareClick(r,c){
  if(!playerSide||waitingForComputer) return;
  const note=notation(r,c);
  const sEl=document.getElementById('inp-start'), eEl=document.getElementById('inp-end');
  const pEl=document.getElementById('inp-piece');
  if(!sEl.value){ sEl.value=note; const p=board[r][c]; if(p!=='e'&&p.startsWith(currentTurn))pEl.value=p[1]; pEl.focus(); }
  else if(!eEl.value){ eEl.value=note; eEl.focus(); }
  else { sEl.value=note; eEl.value=''; const p=board[r][c]; if(p!=='e'&&p.startsWith(currentTurn))pEl.value=p[1]; pEl.focus(); }
  render();
}
function getValidMoves(r,c){
  const p=board[r][c]; if(p==='e'||!p.startsWith(currentTurn)) return [];
  const pt=p[1],enemy=currentTurn==='w'?'b':'w';
  const moves=[],ib=(r,c)=>r>=0&&r<8&&c>=0&&c<8;
  const empty=(r,c)=>board[r][c]==='e';
  const isEnemy=(r,c)=>ib(r,c)&&board[r][c]!=='e'&&board[r][c].startsWith(enemy);
  const free=(r,c)=>ib(r,c)&&(empty(r,c)||isEnemy(r,c));
  const slide=(dr,dc)=>{let nr=r+dr,nc=c+dc;while(ib(nr,nc)){if(empty(nr,nc))moves.push([nr,nc]);else{if(isEnemy(nr,nc))moves.push([nr,nc]);break;}nr+=dr;nc+=dc;}};
  if(pt==='p'){const d=currentTurn==='w'?-1:1,sr=currentTurn==='w'?6:1;if(ib(r+d,c)&&empty(r+d,c)){moves.push([r+d,c]);if(r===sr&&empty(r+2*d,c))moves.push([r+2*d,c]);}if(isEnemy(r+d,c-1))moves.push([r+d,c-1]);if(isEnemy(r+d,c+1))moves.push([r+d,c+1]);}
  if(pt==='c'||pt==='q'){slide(-1,0);slide(1,0);slide(0,-1);slide(0,1);}
  if(pt==='b'||pt==='q'){slide(-1,-1);slide(-1,1);slide(1,-1);slide(1,1);}
  if(pt==='h'){[[-2,-1],[-2,1],[-1,-2],[-1,2],[1,-2],[1,2],[2,-1],[2,1]].forEach(([dr,dc])=>{if(free(r+dr,c+dc))moves.push([r+dr,c+dc]);});}
  if(pt==='k'){[[-1,-1],[-1,0],[-1,1],[0,-1],[0,1],[1,-1],[1,0],[1,1]].forEach(([dr,dc])=>{if(free(r+dr,c+dc))moves.push([r+dr,c+dc]);});}
  return moves;
}
function showPromo(r,c,side){
  const modal=document.getElementById('promo-overlay'), box=document.getElementById('promo-box');
  box.innerHTML='';
  ['q','c','b','h'].forEach(p=>{
    const btn=document.createElement('div'); btn.className='promo-btn'; btn.textContent=SYM[side+p];
    btn.onclick=()=>{ board[r][c]=side+p; modal.classList.remove('show');
      currentTurn=currentTurn==='w'?'b':'w'; updateTurnDisplay(); setStatus("Enter next move"); render(); };
    box.appendChild(btn);
  });
  modal.classList.add('show');
}
function render(){
  const boardEl=document.getElementById('board'); boardEl.innerHTML='';
  const sv=document.getElementById('inp-start').value.trim();
  const selR=sv.length===2?8-parseInt(sv[1]):-1, selC=sv.length===2?sv.charCodeAt(0)-97:-1;
  const vm=(selR>=0&&selC>=0)?getValidMoves(selR,selC):[];
  const vset=new Set(vm.map(([r,c])=>`${r},${c}`));
  for(let r=0;r<8;r++) for(let c=0;c<8;c++){
    const sq=document.createElement('div');
    sq.className='sq '+((r+c)%2===0?'light':'dark');
    if(r===selR&&c===selC)sq.classList.add('selected');
    if(vset.has(`${r},${c}`)) board[r][c]!=='e'?sq.classList.add('valid-capture'):sq.classList.add('valid-move');
    if(board[r][c]!=='e')sq.textContent=SYM[board[r][c]]||board[r][c];
    sq.onclick=()=>handleSquareClick(r,c); boardEl.appendChild(sq);
  }
  document.getElementById('ranks').innerHTML=[8,7,6,5,4,3,2,1].map(n=>`<span>${n}</span>`).join('');
  document.getElementById('files').innerHTML=['a','b','c','d','e','f','g','h'].map(l=>`<span>${l}</span>`).join('');
}
document.addEventListener('keydown',e=>{ if(e.key==='Enter'&&playerSide&&!waitingForComputer)submitMove(); });
resetGame();
</script>
</body>
</html>
"""

# ─── state ────────────────────────────────────────────────────────────────────
_computer: Computer = None
_all_moves: list    = []

def _mat_score(comp_side: str) -> dict:
    from computer import read_board, PIECE_VALUES
    board = read_board()
    human = 'b' if comp_side == 'w' else 'w'
    cs = sum(PIECE_VALUES.get(p[1],0) for p in board.values() if p!='e' and p[0]==comp_side)
    hs = sum(PIECE_VALUES.get(p[1],0) for p in board.values() if p!='e' and p[0]==human)
    return {'computer': cs, 'human': hs, 'diff': cs - hs}

# ─── routes ───────────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template_string(HTML)


@app.route('/start', methods=['POST'])
def start():
    """Initialise the computer for this game."""
    global _computer, _all_moves
    data        = request.get_json() or {}
    human_side  = data.get('side', 'w')
    comp_side   = 'b' if human_side == 'w' else 'w'
    _computer   = Computer(side=comp_side)
    _all_moves  = []
    return jsonify({'ok': True, 'computer_side': comp_side})


@app.route('/move', methods=['POST'])
def move():
    """Human move — delegates to main_play.moveInput()."""
    global _all_moves
    data  = request.get_json()
    if not data:
        return jsonify({'valid': False, 'reason': 'No JSON'}), 400
    side, piece, start, end = data.get('side'), data.get('piece'), data.get('start'), data.get('end')
    if not all([side, piece, start, end]):
        return jsonify({'valid': False, 'reason': 'Missing fields'}), 400
    try:
        valid = main_play.main_play.moveInput(side, piece, start, end)
        if valid:
            _all_moves.append(f"{piece} {start} {end}")
            score = _mat_score(_computer.side) if _computer else None
            return jsonify({'valid': True, 'score': score})
        return jsonify({'valid': False, 'reason': "sorry, that input wasn't correct"})
    except Exception as e:
        return jsonify({'valid': False, 'reason': str(e)}), 500


@app.route('/computer_move', methods=['POST'])
def computer_move():
    """Trigger one computer move."""
    global _all_moves
    if _computer is None:
        return jsonify({'moved': False, 'reason': 'No computer initialised — pick a side first'})
    from computer import read_board, PIECE_VALUES
    board_before = read_board()
    ok = _computer.move()
    if not ok:
        return jsonify({'moved': False, 'reason': 'Computer has no legal moves'})
    board_after = read_board()

    # Work out what the computer played by diffing boards
    pt, start, end, cap = '', '', '', 'e'
    for pos, piece in board_after.items():
        if piece != 'e' and piece[0] == _computer.side:
            if board_before.get(pos, 'e') != piece:
                end = pos; pt = piece[1]
    for pos, piece in board_before.items():
        if piece != 'e' and piece[0] == _computer.side:
            if board_after.get(pos, 'e') == 'e':
                start = pos
    cap = board_before.get(end, 'e') if end else 'e'

    if pt and start and end:
        _all_moves.append(f"{pt} {start} {end}")
        if cap != 'e':
            _computer.reward_capture(cap)

    score = _mat_score(_computer.side)
    return jsonify({'moved': True, 'pt': pt, 'start': start, 'end': end,
                    'captured_piece': cap, 'score': score})


@app.route('/game_over', methods=['POST'])
def game_over():
    """Call when game ends to write score.xlsx and train GNN."""
    if _computer is None:
        return jsonify({'ok': False, 'reason': 'No computer'}), 400
    data = request.get_json() or {}
    won  = data.get('computer_won', False)
    _computer.record_outcome(won=won, all_moves=_all_moves)
    score_print_summary()
    return jsonify({'ok': True})


@app.route('/reset', methods=['POST'])
def reset():
    global _computer, _all_moves
    _computer  = None
    _all_moves = []
    try:
        csv_setup.csv_setup.setup()
    except Exception as e:
        return jsonify({'ok': False, 'reason': str(e)}), 500
    return jsonify({'ok': True})


@app.route('/health')
def health():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    try:
        csv_setup.csv_setup.setup()
        print("[chess] Board reset OK")
    except Exception as e:
        print(f"[chess] Board reset warning: {e}")
    print("\n[chess] Open http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)