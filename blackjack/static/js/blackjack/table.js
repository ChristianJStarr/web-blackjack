import {createElement} from "./utility.js";
import {Dealer} from "./dealer.js";
import {Seats} from "./seats.js";
import {Bank} from "./bank.js";
import {Actions} from "./actions.js";
import {Message} from "./message.js";
import {History} from "./history.js";
import {Shoe} from "./shoe.js";
import {Control} from "./control.js";

export class Table {

    constructor(game=null) {
        this.game = game;
        this.node = game.node.querySelector('.table');

        this.history = new History(this, 'dealer');
        this.dealer = new Dealer(this);
        this.shoe = new Shoe(this);
        this.seats = new Seats(this);
        this.bank = new Bank(this);
        this.actions = new Actions(this);
        this.message = new Message(this);
        this.control = new Control(this);
        this.chips = [];

        this.loading_node = createElement('div', 'loading');
        this.loading_node.textContent = 'Loading table...';
        this.loading_node.classList.add('-show');
        const minLoadingTime = 2000;
        const startTime = Date.now();

        const checkState = setInterval(() => {
            const elapsedTime = Date.now() - startTime;
            if (this.game.state && elapsedTime >= minLoadingTime) {
                this.loading_node.classList.remove('-show');
                clearInterval(checkState);
            }
        }, 100);


        this.node.append(
            this.loading_node,
            this.history.node,
            this.dealer.node,
            this.shoe.node,
            this.message.node,
            this.seats.node,
            this.control.node,
            this.actions.node,
            this.bank.node,
        )

    }

    action(action, data=null) {
        this.game.action(action, data)
    }
    sound(type) {
        if (this.game) {
            this.game.sound(type);
        }
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