class ProgressManager {
	// activeTasks is an internal counter, NOT a reactive state, to prevent accidental circular reactive updates
	private activeTasks = 0;
	private progress = $state(0);
	private isVisible = $state(false);
	private timer: any = null;
	private finishTimer: any = null;

	get current(): number {
		return this.progress;
	}

	get visible(): boolean {
		return this.isVisible;
	}

	start() {
		this.activeTasks += 1;
		if (this.activeTasks === 1) {
			this.beginAnimation();
		}
	}

	done() {
		if (this.activeTasks > 0) {
			this.activeTasks -= 1;
		}

		if (this.activeTasks === 0) {
			this.finishAnimation();
		}
	}

	private beginAnimation() {
		if (this.finishTimer) {
			clearTimeout(this.finishTimer);
			this.finishTimer = null;
		}

		this.progress = 20;
		this.isVisible = true;

		if (this.timer) clearInterval(this.timer);

		this.timer = setInterval(() => {
			if (this.progress < 65) {
				this.progress += Math.random() * 12;
			} else if (this.progress < 85) {
				this.progress += Math.random() * 5;
			} else if (this.progress < 95) {
				this.progress += Math.random() * 1.2;
			}
		}, 180);
	}

	private finishAnimation() {
		if (this.timer) {
			clearInterval(this.timer);
			this.timer = null;
		}

		this.progress = 100;

		this.finishTimer = setTimeout(() => {
			this.isVisible = false;
			this.progress = 0;
			this.finishTimer = null;
		}, 300);
	}
}

export const progress = new ProgressManager();
