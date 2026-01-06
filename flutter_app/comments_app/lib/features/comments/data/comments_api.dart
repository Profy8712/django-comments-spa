import 'package:dio/dio.dart';

import 'captcha_data.dart';

class CommentsApi {
  final Dio _dio;

  CommentsApi(this._dio);

  /// GET /api/comments/
  /// Common params: page, ordering
  Future<Map<String, dynamic>> fetchComments({
    int page = 1,
    String? ordering,
  }) async {
    final resp = await _dio.get(
      '/api/comments/',
      queryParameters: {
        'page': page,
        if (ordering != null && ordering.isNotEmpty) 'ordering': ordering,
      },
    );

    if (resp.data is Map<String, dynamic>) {
      return resp.data as Map<String, dynamic>;
    }
    throw StateError('Unexpected response type: ${resp.data.runtimeType}');
  }

  /// GET /api/comments/captcha/
  Future<CaptchaData> fetchCaptcha() async {
    final resp = await _dio.get('/api/comments/captcha/');

    if (resp.data is Map<String, dynamic>) {
      return CaptchaData.fromJson(resp.data as Map<String, dynamic>);
    }
    throw StateError('Unexpected captcha response type: ${resp.data.runtimeType}');
  }
}
