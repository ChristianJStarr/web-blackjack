import {Chip} from "./chip.js";
import {arraysEqual, createElement} from "./utility.js";

export class Bank {

    constructor(table) {
        this.table = table;
        this.chips = [];
        this.balance = 0;
        this.bet = 0;

        this.node = createElement('div', 'bank');
        this.chips_node = createElement('div', 'bank__chips');
        this.balance_node = createElement('div', 'bank__balance');

        this.header_balance = document.querySelector('.header__balance');

        this.balance_node.textContent = `$${this.balance}`;

        this.node.append(
            this.chips_node,
            this.balance_node
        );

        this.debounceTimeout = null;
        this.debounceDelay = 300;
        this.pendingBetAmount = null;
    }

    updateBalance(balance) {
        this.balance_node.textContent = `$${this.balance}`;
        if (this.header_balance) {
            this.header_balance.textContent = `$${this.balance}`;
        }
        this.balance = balance;
    }

    updateChips(chips) {
        for (const chip_value of chips) {
            const chip_object = new Chip(chip_value);

            chip_object.node.onclick = this.debounce(() => {
                this.pendingBetAmount += chip_value;
                this.processBet();
            }, this.debounceDelay);
            this.chips_node.append(chip_object.node)
        }
        this.chips = chips;
    }

    processBet() {
        if (this.pendingBetAmount !== null) {
            this.table.action('player_bet', { amount: this.pendingBetAmount });
            this.pendingBetAmount = null;
        }
    }

    debounce(func, delay) {
        return (...args) => {
            if (this.debounceTimeout) {
                clearTimeout(this.debounceTimeout);
            }
            this.debounceTimeout = setTimeout(() => func(...args), delay);
        };
    }

    update(state) {

        const chips = state?.chips ?? [];
        const balance = state?.balance ?? 0;

        chips.sort((a, b) => a - b);

        if(!arraysEqual(this.chips, chips)) {
            this.updateChips(chips);
        }

        if(balance !== this.balance) {
            this.updateBalance(balance);
        }
    }
}