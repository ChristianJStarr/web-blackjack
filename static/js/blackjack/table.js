import {createElement} from "./utility.js";
import {Dealer} from "./dealer.js";
import {Seats} from "./seats.js";
import {Bank} from "./bank.js";
import {Actions} from "./actions.js";
import {Message} from "./message.js";
import {History} from "./history.js";
import {Shoe} from "./shoe.js";

export class Table {

    constructor(game=null) {
        this.game = game;
        this.node = createElement('div', 'table');

        this.history = new History(this, 'dealer');
        this.dealer = new Dealer(this);
        this.shoe = new Shoe(this);
        this.seats = new Seats(this);
        this.bank = new Bank(this);
        this.actions = new Actions(this);
        this.message = new Message(this);
        this.chips = [];

        this.node.append(
            this.history.node,
            this.dealer.node,
            this.shoe.node,
            this.message.node,
            this.seats.node,
            this.actions.node,
            this.bank.node,
        )

    }

    action(action, data=null) {
        this.game.action(action, data)
    }
    update(state) {
        this.chips = state?.chips ?? [];
        this.history.update(state);
        this.dealer.update(state);
        this.shoe.update(state);
        this.message.update(state);
        this.seats.update(state);
        this.bank.update(state);
        this.actions.update(state);
    }
}