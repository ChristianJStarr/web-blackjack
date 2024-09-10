import {arraysEqual, createElement} from "./utility.js";

export class Actions {
    constructor(table) {
        this.table = table;
        this.node = createElement('div', 'actions');
        this.actions = [];

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
        let seat_id = 0;
        for (const seat of state?.seats ?? []) {
           if (seat.player?.id === this.table.game.player_id) {
                seat_id = seat.id;
            }
        }

        const is_turn = state?.turn === seat_id;
        if (!arraysEqual(actions, this.actions)) {
            this.node.replaceChildren();
            for (const [index, action] of actions.entries()) {
                const action_node = createElement('button', `action -${action}`);
                action_node.onclick = this.debounce(() => {
                    this.pendingAction = action;
                    this.playerAction();
                }, this.debounceDelay);
                action_node.textContent = action;
                this.node.append(action_node);
            }
            this.actions = actions;
        }
        if(state?.turn !== 0) {
            for (const action_node of this.node.children) {
                action_node.style.display = is_turn ? 'block' : 'none';
            }
        }
    }
}