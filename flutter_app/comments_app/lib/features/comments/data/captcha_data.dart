class CaptchaData {
  final String key;
  final String image;

  /// `image` can be an URL or base64 string depending on backend.
  CaptchaData({required this.key, required this.image});

  factory CaptchaData.fromJson(Map<String, dynamic> json) {
    final key = (json['key'] ?? json['captcha_key'] ?? '').toString();
    final image = (json['image'] ?? json['image_url'] ?? json['captcha_image'] ?? '').toString();
    return CaptchaData(key: key, image: image);
  }
}
