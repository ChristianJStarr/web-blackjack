import {createElement} from "./utility.js";

export class Actions {
    constructor() {
        this.node = createElement('div', 'actions');
        this.actions = [];
    }

    update(state) {
        const actions = state?.actions ?? [];

        if (actions !== this.actions) {
            this.node.replaceChildren();
            for (const [index, action] of actions.entries()) {
                const action_node = createElement('button', `action -${action}`);
                action_node.onclick = event => {
                    this.table.action(action);
                }
            }
            this.actions = actions;
        }
    }
}