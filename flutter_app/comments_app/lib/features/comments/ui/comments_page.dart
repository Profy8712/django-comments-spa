import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../../../core/http_client.dart';
import '../data/comments_api.dart';
import 'form/add_comment_page.dart';

class CommentsPage extends StatefulWidget {
  const CommentsPage({super.key});

  @override
  State<CommentsPage> createState() => _CommentsPageState();
}

class _CommentsPageState extends State<CommentsPage> {
  late final Dio _dio;
  late final CommentsApi _api;

  bool _loading = true;
  String? _error;

  int _page = 1;
  String _ordering = '-created_at'; // LIFO by default
  List<dynamic> _items = [];

  @override
  void initState() {
    super.initState();
    _dio = createDio();
    _api = CommentsApi(_dio);
    _load();
  }

  Future<void> _load() async {
    setState(() {
      _loading = true;
      _error = null;
    });

    try {
      final data = await _api.fetchComments(page: _page, ordering: _ordering);
      final results = (data['results'] as List?) ?? [];
      setState(() {
        _items = results;
        _loading = false;
      });
    } catch (e) {
      setState(() {
        _error = e.toString();
        _loading = false;
      });
    }
  }

  void _setOrdering(String value) {
    setState(() {
      _ordering = value;
      _page = 1;
    });
    _load();
  }

  Future<void> _openAdd() async {
    await Navigator.of(context).push(
      MaterialPageRoute(builder: (_) => const AddCommentPage()),
    );
    // after return, refresh list
    await _load();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Comments'),
        actions: [
          IconButton(
            onPressed: _openAdd,
            icon: const Icon(Icons.add),
            tooltip: 'Add comment',
          ),
          PopupMenuButton<String>(
            onSelected: _setOrdering,
            itemBuilder: (context) => const [
              PopupMenuItem(value: '-created_at', child: Text('Date ↓ (LIFO)')),
              PopupMenuItem(value: 'created_at', child: Text('Date ↑')),
              PopupMenuItem(value: 'username', child: Text('User A–Z')),
              PopupMenuItem(value: '-username', child: Text('User Z–A')),
              PopupMenuItem(value: 'email', child: Text('Email A–Z')),
              PopupMenuItem(value: '-email', child: Text('Email Z–A')),
            ],
          ),
        ],
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Text(_error!, style: const TextStyle(color: Colors.red)),
                  ),
                )
              : Column(
                  children: [
                    Expanded(
                      child: ListView.separated(
                        itemCount: _items.length,
                        separatorBuilder: (_, __) => const Divider(height: 1),
                        itemBuilder: (context, index) {
                          final item = _items[index];
                          return ListTile(
                            title: Text(item['username'] ?? '—'),
                            subtitle: Text('${item['email'] ?? ''}\n${item['text'] ?? ''}'),
                            isThreeLine: true,
                          );
                        },
                      ),
                    ),
                    Padding(
                      padding: const EdgeInsets.all(12),
                      child: Row(
                        children: [
                          ElevatedButton(
                            onPressed: _page > 1
                                ? () {
                                    setState(() => _page--);
                                    _load();
                                  }
                                : null,
                            child: const Text('Prev'),
                          ),
                          const SizedBox(width: 12),
                          ElevatedButton(
                            onPressed: () {
                              setState(() => _page++);
                              _load();
                            },
                            child: const Text('Next'),
                          ),
                          const Spacer(),
                          Text('Page $_page'),
                        ],
                      ),
                    ),
                  ],
                ),
    );
  }
}
