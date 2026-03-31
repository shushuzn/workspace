/**
 * Operation Base Class
 * Standard interface for all operations
 */

export class Operation {
  constructor(id, name, type = 'productive') {
    this.id = id;
    this.name = name;
    this.type = type; // 'productive' or 'detection'
    this.weight = 1.0;
  }

  async execute() {
    throw new Error('Operation.execute() must be implemented');
  }

  canImprove() {
    return true; // Override in subclass
  }
}

export class DetectionOperation extends Operation {
  constructor(id, name) {
    super(id, name, 'detection');
  }

  // For detection ops, success means finding something
  isSuccess(result) {
    return result.missing > 0 || result.changed > 0 ||
           result.ideas > 0 || result.found > 0 ||
           result.committed > 0;
  }
}

export class ProductiveOperation extends Operation {
  constructor(id, name) {
    super(id, name, 'productive');
  }

  // For productive ops, success means making progress
  isSuccess(result) {
    return result.created > 0 || result.cleaned > 0 ||
           result.deleted > 0 || result.found > 0 ||
           result.success === true || result.committed > 0;
  }
}
