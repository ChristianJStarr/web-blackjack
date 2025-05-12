import {createElement} from "./utility.js";

export class History {

    constructor(table=null, type) {
        this.table = table;
        this.node = createElement('div', `history -${type}`);
        this.results_node = createElement('div', 'history__results');
        this.text_node = createElement('p', 'history__label');

        this.text_node.textContent = `${type} History`;

        this.node.append(
            this.text_node,
            this.results_node,
        )
    }


    update(state) {
        const history = state?.dealer?.history ?? [];
        if(history !== this.history) {
            this.setHistory(history);
        }
    }


    setHistory(history) {
        if(history) {
            this.results_node.replaceChildren();
            for (const result of history.reverse()) {
                const result_node = createElement('div', `history__result -${result}`);
                result_node.textContent = result;

                this.results_node.append(result_node);
            }
        }else {
            this.results_node.replaceChildren();
        }
        this.history = history;
    }
}