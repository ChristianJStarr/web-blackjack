import {createElement} from "./utility.js";
import {Dealer} from "./dealer.js";
import {Seats} from "./seats.js";
import {Bank} from "./bank.js";
import {Actions} from "./actions.js";

export class Table {

    constructor(game=null) {
        this.game = game;
        this.node = createElement('div', 'table');

        this.dealer = new Dealer(this);
        this.seats = new Seats(this);
        this.bank = new Bank(this);
        this.actions = new Actions(this);

        this.node.append(
            this.dealer.node,
            this.seats.node,
            this.bank.node,
            this.actions.node
        )

    }

    action(action, data=null) {
        this.game.action(action, data)
    }
    update(state) {
        this.dealer.update(state);
        this.seats.update(state);
        this.bank.update(state);
        this.actions.update(state);
    }
}