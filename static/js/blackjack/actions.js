import {arraysEqual, createElement} from "./utility.js";

export class Actions {
    constructor(table) {
        this.table = table;
        this.node = createElement('div', 'actions');

        this.actions_node = createElement('div', 'actions__buttons');
        this.actions = [];

        this.timer_node = createElement('div', 'actions__timer');
        const time = 65;
        this.timer_node.style = `--time: ${time}%;`;

        this.node.append(
            this.actions_node,
            this.timer_node,
        );

        this.debounceTimeout = null;
        this.debounceDelay = 300;
        this.pendingAction = null;
    }

    debounce(func, delay) {
        return (...args) => {
            if (this.debounceTimeout) {
                clearTimeout(this.debounceTimeout);
            }
            this.debounceTimeout = setTimeout(() => func(...args), delay);
        };
    }

    playerAction() {
        if (this.pendingAction !== null) {
            this.table.action('player_action', this.pendingAction);
            this.pendingAction = null;
        }
    }

    update(state) {
        const actions = state?.actions ?? [];
        let seat_id = this.table.game.seat_id;

        const is_turn = state?.turn === seat_id;
        if (!arraysEqual(actions, this.actions)) {
            this.actions_node.replaceChildren();
            for (const [index, action] of actions.entries()) {
                const action_node = createElement('button', `actions__button -${action}`);
                action_node.onclick = this.debounce(() => {
                    if (action === 'repeat bet') {
                        this.table.sound('chip');
                    }
                    this.pendingAction = action;
                    this.playerAction();
                    this.node.classList.remove('-is_turn');
                }, this.debounceDelay);
                action_node.textContent = action;
                this.actions_node.append(action_node);
            }
            this.actions = actions;
        }
        if(state?.turn !== 0) {
            if(is_turn) {
                this.node.classList.add('-is_turn');
            }else {
                this.node.classList.remove('-is_turn');
            }
        }
    }
}