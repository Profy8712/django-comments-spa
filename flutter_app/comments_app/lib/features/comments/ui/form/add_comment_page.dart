import 'dart:convert';

import 'package:flutter/material.dart';
import 'package:dio/dio.dart';

import '../../../../core/config.dart';
import '../../../../core/http_client.dart';
import '../../data/comments_api.dart';
import '../../data/captcha_data.dart';

class AddCommentPage extends StatefulWidget {
  const AddCommentPage({super.key});

  @override
  State<AddCommentPage> createState() => _AddCommentPageState();
}

class _AddCommentPageState extends State<AddCommentPage> {
  late final Dio _dio;
  late final CommentsApi _api;

  final _formKey = GlobalKey<FormState>();

  final _username = TextEditingController();
  final _email = TextEditingController();
  final _homepage = TextEditingController();
  final _text = TextEditingController();
  final _captchaAnswer = TextEditingController();

  bool _loadingCaptcha = true;
  String? _captchaError;
  CaptchaData? _captcha;

  @override
  void initState() {
    super.initState();
    _dio = createDio();
    _api = CommentsApi(_dio);
    _loadCaptcha();
  }

  @override
  void dispose() {
    _username.dispose();
    _email.dispose();
    _homepage.dispose();
    _text.dispose();
    _captchaAnswer.dispose();
    super.dispose();
  }

  Future<void> _loadCaptcha() async {
    setState(() {
      _loadingCaptcha = true;
      _captchaError = null;
    });

    try {
      final c = await _api.fetchCaptcha();
      setState(() {
        _captcha = c;
        _loadingCaptcha = false;
      });
    } catch (e) {
      setState(() {
        _captchaError = e.toString();
        _loadingCaptcha = false;
      });
    }
  }

  String _resolveCaptchaImageUrl(String raw) {
    // Backend returns either:
    // 1) full URL (http/https)
    // 2) relative URL like "/captcha/image/<key>/"
    // 3) base64 (optional future)
    if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
    if (raw.startsWith('/')) return '${AppConfig.apiBaseUrl}$raw';
    return raw;
  }

  Widget _captchaWidget() {
    if (_loadingCaptcha) {
      return const Center(child: CircularProgressIndicator());
    }
    if (_captchaError != null) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Captcha error: $_captchaError', style: const TextStyle(color: Colors.red)),
          const SizedBox(height: 8),
          ElevatedButton(onPressed: _loadCaptcha, child: const Text('Retry')),
        ],
      );
    }

    final c = _captcha!;
    final raw = c.image.trim();

    // If relative or absolute URL -> show Image.network
    final isUrl = raw.startsWith('/') || raw.startsWith('http://') || raw.startsWith('https://');

    // If base64 -> show memory
    final isBase64 = !isUrl && raw.isNotEmpty;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          children: [
            const Text('CAPTCHA', style: TextStyle(fontWeight: FontWeight.w600)),
            const Spacer(),
            IconButton(
              onPressed: _loadCaptcha,
              icon: const Icon(Icons.refresh),
              tooltip: 'Refresh CAPTCHA',
            ),
          ],
        ),
        const SizedBox(height: 8),
        if (isUrl)
          Image.network(_resolveCaptchaImageUrl(raw), height: 60)
        else if (isBase64)
          Builder(
            builder: (_) {
              try {
                final normalized = raw.startsWith('data:image')
                    ? raw.substring(raw.indexOf('base64,') + 7)
                    : raw;
                final bytes = base64Decode(normalized);
                return Image.memory(bytes, height: 60);
              } catch (e) {
                return Text(
                  'Captcha is not a URL and not valid base64.\n$e\nValue: $raw',
                  style: const TextStyle(color: Colors.red),
                );
              }
            },
          )
        else
          const Text('No CAPTCHA image received', style: TextStyle(color: Colors.red)),
        const SizedBox(height: 8),
        TextFormField(
          controller: _captchaAnswer,
          decoration: const InputDecoration(
            labelText: 'CAPTCHA Answer',
            border: OutlineInputBorder(),
          ),
          validator: (v) {
            if (v == null || v.trim().isEmpty) return 'CAPTCHA is required';
            return null;
          },
        ),
      ],
    );
  }

  void _submitStub() {
    if (!_formKey.currentState!.validate()) return;

    final key = _captcha?.key ?? '';
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Form values (stub)'),
        content: SelectableText(
          'username=${_username.text}\n'
          'email=${_email.text}\n'
          'homepage=${_homepage.text}\n'
          'text=${_text.text}\n'
          'captcha_key=$key\n'
          'captcha_answer=${_captchaAnswer.text}\n\n'
          'Next step: implement POST /api/comments/',
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(context), child: const Text('OK')),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Add Comment')),
      body: Padding(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: ListView(
            children: [
              TextFormField(
                controller: _username,
                decoration: const InputDecoration(labelText: 'User Name', border: OutlineInputBorder()),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'User Name is required';
                  final ok = RegExp(r'^[a-zA-Z0-9]+$').hasMatch(v.trim());
                  if (!ok) return 'Only латинские буквы и цифры';
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _email,
                decoration: const InputDecoration(labelText: 'E-mail', border: OutlineInputBorder()),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'E-mail is required';
                  final ok = RegExp(r'^[^@\s]+@[^@\s]+\.[^@\s]+$').hasMatch(v.trim());
                  if (!ok) return 'Invalid email format';
                  return null;
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _homepage,
                decoration: const InputDecoration(labelText: 'Home page (optional)', border: OutlineInputBorder()),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _text,
                minLines: 4,
                maxLines: 8,
                decoration: const InputDecoration(labelText: 'Text', border: OutlineInputBorder()),
                validator: (v) {
                  if (v == null || v.trim().isEmpty) return 'Text is required';
                  return null;
                },
              ),
              const SizedBox(height: 16),
              _captchaWidget(),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _submitStub,
                child: const Text('Submit (stub)'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
