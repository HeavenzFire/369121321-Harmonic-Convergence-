/**
 * Bayesian Success Tracker for Resonant Atlas Node
 * Tracks success/failure rates and calculates probabilities for adaptive behavior
 */

class BayesianTracker {
  constructor() {
    this.operations = new Map(); // operation -> {success: count, failure: count, lastUpdate: timestamp}
    this.persistenceFile = '/vercel/sandbox/resonant-atlas-node/data/bayesian_state.json';
    this.loadState();
  }

  // Update success/failure for an operation
  update(operation, success) {
    if (!this.operations.has(operation)) {
      this.operations.set(operation, { success: 0, failure: 0, lastUpdate: Date.now() });
    }

    const op = this.operations.get(operation);
    if (success) {
      op.success++;
    } else {
      op.failure++;
    }
    op.lastUpdate = Date.now();

    this.saveState();
  }

  // Calculate success probability using Laplace smoothing
  getProbability(operation) {
    const op = this.operations.get(operation);
    if (!op) return 0.5; // Default prior

    const total = op.success + op.failure;
    if (total === 0) return 0.5;

    // Laplace smoothing: add 1 to both numerator and denominator
    return (op.success + 1) / (total + 2);
  }

  // Get suggested retry parameters based on probability
  getRetryParams(operation) {
    const prob = this.getProbability(operation);
    const op = this.operations.get(operation);

    // Adaptive retry logic
    const baseRetries = 3;
    const maxRetries = 10;
    const minRetries = 1;

    // Higher probability = fewer retries needed
    // Lower probability = more retries needed
    let retries = Math.round(baseRetries / prob);
    retries = Math.max(minRetries, Math.min(maxRetries, retries));

    // Timeout scaling (lower prob = longer timeouts)
    const baseTimeout = 1000; // 1 second
    const timeout = baseTimeout * (2 - prob); // Scale from 1x to 2x

    // Backoff multiplier (more aggressive for low success rates)
    const backoff = prob < 0.5 ? 2.0 : 1.5;

    return {
      retries,
      timeout: Math.round(timeout),
      backoff,
      confidence: prob,
      totalObservations: (op?.success || 0) + (op?.failure || 0)
    };
  }

  // Get all operations with their stats
  getAllStats() {
    const stats = {};
    for (const [op, data] of this.operations) {
      stats[op] = {
        ...data,
        probability: this.getProbability(op),
        retryParams: this.getRetryParams(op)
      };
    }
    return stats;
  }

  // Load state from file
  async loadState() {
    try {
      const fs = require('fs').promises;
      const data = await fs.readFile(this.persistenceFile, 'utf8');
      const state = JSON.parse(data);
      this.operations = new Map(Object.entries(state));
    } catch (error) {
      // File doesn't exist or corrupted, start fresh
      console.log('Bayesian tracker: Starting with fresh state');
    }
  }

  // Save state to file
  async saveState() {
    try {
      const fs = require('fs').promises;
      const state = Object.fromEntries(this.operations);
      await fs.writeFile(this.persistenceFile, JSON.stringify(state, null, 2));
    } catch (error) {
      console.error('Failed to save Bayesian state:', error);
    }
  }

  // Clean up old operations (older than 30 days)
  cleanup(maxAge = 30 * 24 * 60 * 60 * 1000) {
    const now = Date.now();
    for (const [op, data] of this.operations) {
      if (now - data.lastUpdate > maxAge) {
        this.operations.delete(op);
      }
    }
    this.saveState();
  }
}

module.exports = new BayesianTracker();