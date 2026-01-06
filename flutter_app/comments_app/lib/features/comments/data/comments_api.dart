import 'package:dio/dio.dart';

class CommentsApi {
  final Dio _dio;

  CommentsApi(this._dio);

  /// Fetch comments list from:
  /// GET /api/comments/
  ///
  /// Supports common query params (depending on backend):
  /// - page
  /// - ordering (e.g. "created_at", "-created_at", "username", "-username", "email", "-email")
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
}
