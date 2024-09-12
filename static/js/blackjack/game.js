import { Table } from "./table.js";
import {createElement} from "./utility.js";

export class Game {

    constructor() {
        this.id = window.location.pathname.split('/').pop();
        this.role = window.location.pathname.includes('/spectate') ? 'spectator' : 'player';
        this.user_id = localStorage.getItem('user_id');
        this.processing_state = false;
        this.state_queue = [];
        this.state = {};

        this.node = document.querySelector('.game');
        this.table = new Table(this);
        this.node.append(this.table.node);
        this.audio_enabled = false;

        this.connect();

        this.sounds = {
            chip: [
                new Audio('/static/sounds/chip_1.wav'),
                new Audio('/static/sounds/chip_2.wav'),
            ],
            card: [
                new Audio('/static/sounds/card_1.wav'),
                new Audio('/static/sounds/card_2.wav'),
                new Audio('/static/sounds/card_3.wav'),
            ],
            win: [
                new Audio('/static/sounds/win.wav'),
            ],
            lose: [
                new Audio('/static/sounds/lose.wav'),
            ],
            blackjack: [
                new Audio('/static/sounds/blackjack.wav'),
            ],
        }


    }

    //---------------------------------------
    // Game Methods
    //---------------------------------------
    connect() {
        this.socket = io.connect('http://' + document.domain + ':' + '5000');
        if(this.socket) {
            this.socket.on('connect', (data)=> { this.onConnect(this,data) });
            this.socket.on('disconnect', (data)=> { this.onDisconnect(this,data) });
            this.socket.on('join_game', (data)=> { this.onJoinGame(this,data) });
            this.socket.on('game_state', (data)=> { this.onGameState(this,data) });
            this.socket.on('player_bet', (data)=> { this.onPlayerBet(this,data) });
            this.socket.on('player_bust', (data)=> { this.onPlayerBust(this,data) });
            this.socket.on('player_blackjack', (data)=> { this.onPlayerBlackjack(this,data) });
            this.socket.on('round_result', (data)=> { this.onRoundResult(this,data) });
            this.socket.on('message', (data)=> { this.onPlayerMessage(this,data) });
        }
    }
    disconnect() {
        this.socket.emit('disconnect');
    }
    joinGame() {
        this.socket.emit('join_game',this.role)
    }
    action(action, data=null) {
        this.socket.emit(action, data ? data : {});
    }
    sound(type) {
        const sounds = this.sounds[type];
        if(sounds && this.audio_enabled) {
            const sound = sounds[Math.floor(Math.random()*sounds.length)]
            sound.play();
        }
    }


    //---------------------------------------
    // Socket Events
    //---------------------------------------
    onConnect(game, data={}) {
        game.joinGame();
    }
    onDisconnect(game, data={}) {
    }
    onJoinGame(game, data={}) {
        game.seat_id = data.seat_id ?? 0;
        game.role = data?.role ?? 'spectator';
        game.addState(game.state, true);
    }
    onGameState(game, data={}) {
        game.addState(data);
    }
    onPlayerBet(game, data={}) {
        if(data?.success) {

        }
    }
    onRoundResult(game, data={}) {
        game.balance = data?.balance ?? 0;
        game.table.bank.updateBalance(game.balance);
        game.table.message.update(data);
        game.sound(data?.result);
    }
    onPlayerMessage(game, data) {
        game.table.message.setTempMessage(data, 1000);
    }
    onPlayerBust(game, data) {
        game.table.message.setTempMessage(data, 1000);
        game.sound('lose');
    }
    onPlayerBlackjack(game, data) {
        game.table.message.setTempMessage(data?.message,1000);
        game.balance = data?.balance ?? 0;
        game.table.bank.updateBalance(game.balance);
        game.sound('blackjack');
    }


    //---------------------------------------
    // State Management
    //---------------------------------------
    async processStateQueue(force=false) {
        if ((this.processing_state || this.state_queue.length === 0) && !force) return;

        this.processing_state = true;
        while (this.state_queue.length > 0) {
            const {state, resolve} = this.state_queue.shift();

            try {
                const current_state_json = JSON.stringify(this.state);
                const new_state_json = JSON.stringify(state);

                if(force || current_state_json !== new_state_json) {
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
    addState(state, force=false) {
        return new Promise((resolve) => {
            this.state_queue.push({ state, resolve });
            this.processStateQueue(force);
        });
    }
    processState(state) {
        this.state = state;
        this.table.update(state);
    }

}