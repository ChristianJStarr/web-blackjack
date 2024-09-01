import { Table } from "./table.js";

export class Game {

    constructor() {
        this.id = window.location.pathname.split('/').pop();
        this.role = window.location.pathname.includes('/spectate') ? 'spectator' : 'player';
        this.player_id = localStorage.getItem('player-id');
        this.processing_state = false;
        this.state_queue = [];
        this.table = new Table(this);

        this.node = document.querySelector('.game');
        this.node.append(this.table.node);

        this.connect();
    }

    //---------------------------------------
    // Game Methods
    //---------------------------------------
    connect() {
        this.socket = io.connect('http://' + document.domain + ':' + '5000');
        if(this.socket) {
            this.socket.on('connect', (data)=> { this.onConnect(this,data) });
            this.socket.on('disconnect', (data)=> { this.onDisconnect(this,data) });
            this.socket.on('player_assigned', (data)=> { this.onPlayerAssigned(this,data) });
            this.socket.on('game_state', (data)=> { this.onGameState(this,data) });
            this.socket.on('player_bet', (data)=> { this.onPlayerBet(this,data) });
            this.socket.on('round_result', (data)=> { this.onRoundResult(this,data) });
        }
    }
    disconnect() {
        this.socket.emit('disconnect');
    }
    joinGame() {
        this.socket.emit({
            game_id: this.id,
            player_id: this.player_id,
            role: this.role
        })
    }
    action(action, data=null) {
        this.socket.emit(action, data ? data : {});
    }


    //---------------------------------------
    // Socket Events
    //---------------------------------------
    onConnect(game, data={}) {
        game.joinGame();
    }
    onDisconnect(game, data={}) {}
    onPlayerAssigned(game, data={}) {
        game.player_id = data.player_id;
        game.seat_id = data.seat_id ? data.seat_id : 0;
        game.balance = data.balance ? data.balance : 0;
    }
    onGameState(game, data={}) {
        game.addState(data);
    }
    onPlayerBet(game, data={}) {}
    onRoundResult(game, data={}) {}


    //---------------------------------------
    // State Management
    //---------------------------------------
    async processStateQueue() {
        if (this.processing_state || this.state_queue.length === 0) return;

        this.processing_state = true;
        while (this.state_queue.length > 0) {
            const {state, resolve} = this.state_queue.shift();

            try {
                const current_state_json = JSON.stringify(this.state);
                const new_state_json = JSON.stringify(state);

                if(current_state_json !== new_state_json) {
                    await this.processState(state);
                }
            } catch (error) {
                console.error('Error applying updates:', error);
            } finally {
                resolve();
            }
        }
        this.processing_state = false;
    }
    addState(state) {
        return new Promise((resolve) => {
            this.state_queue.push({ state, resolve });
            this.processStateQueue();
        });
    }
    processState(state) {
        this.table.update(state);
    }

}