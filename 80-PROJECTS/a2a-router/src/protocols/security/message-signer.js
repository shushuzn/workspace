import crypto from 'crypto';

export class MessageSigner {
  generateKeyId() {
    return 'a2a_kid_' + crypto.randomBytes(16).toString('hex');
  }

  generateApiKey() {
    return 'a2a_sk_' + crypto.randomBytes(32).toString('hex');
  }

  sign(apiKey, message) {
    const data = message.id + message.timestamp + JSON.stringify(message.payload);
    return crypto.createHmac('sha256', apiKey).update(data).digest('hex');
  }

  verify(apiKey, message, signature) {
    if (!signature || signature.length !== 64) {
      return false;
    }
    const expected = this.sign(apiKey, message);
    try {
      return crypto.timingSafeEqual(
        Buffer.from(signature, 'hex'),
        Buffer.from(expected, 'hex')
      );
    } catch {
      return false;
    }
  }
}
