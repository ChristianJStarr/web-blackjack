import {Chip} from "./chip.js";
import {createElement} from "./utility.js";

export class Bank {

    constructor(table) {
        this.table = table;
        this.chips = {};
        this.balance = 0;

        this.node = createElement('div', 'bank');
        this.chips_node = createElement('div', 'bank__chips');
        this.balance_node = createElement('div', 'bank__balance');

        this.header_balance = document.querySelector('.header__balance');

        this.balance_node.textContent = `$${this.balance}`;

        this.node.append(
            this.chips_node,
            this.balance_node
        );
    }

    updateBalance(balance) {
        if(balance !== this.balance) {
            this.balance = balance;
            this.balance_node.textContent = `$${this.balance}`;
            if (this.header_balance) {
                this.header_balance.textContent = `$${this.balance}`;
            }
        }
    }

    update(state) {
        if (!this.chips_node.children.length) {
            const chips = state?.chips ?? [];

            for (const chip_value of chips) {
                const chip_object = new Chip(chip_value);

                chip_object.node.onclick = event => {
                    this.table.action('player_bet', { amount: chip_value });
                }
                this.chips[chip_value] = chip_object;
                this.chips_node.append(chip_object.node)
            }
        }
    }
}