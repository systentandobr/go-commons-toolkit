package utils

import (
	"context"
	"io"
	"os"
	"time"

	"go.uber.org/zap"
	"go.uber.org/zap/zapcore"
)

// Logger defines logging operations
type Logger interface {
	Debug(msg string, fields ...Field)
	Info(msg string, fields ...Field)
	Warn(msg string, fields ...Field)
	Error(msg string, fields ...Field)
	Fatal(msg string, fields ...Field)
	With(fields ...Field) Logger
	WithContext(ctx context.Context) Logger
}

// Field represents a log field
type Field struct {
	Key   string
	Value interface{}
}

// Config holds logger configuration
type Config struct {
	Level      string
	Format     string
	Output     io.Writer
	TimeFormat string
}

// DefaultConfig returns default logger configuration
func DefaultConfig() Config {
	return Config{
		Level:      "info",
		Format:     "json",
		Output:     os.Stdout,
		TimeFormat: time.RFC3339,
	}
}

// ZapLogger implements Logger using zap
type ZapLogger struct {
	logger *zap.Logger
}

// New creates a new logger instance
func New(config Config) (Logger, error) {
	// Set log level
	var level zapcore.Level
	switch config.Level {
	case "debug":
		level = zapcore.DebugLevel
	case "info":
		level = zapcore.InfoLevel
	case "warn":
		level = zapcore.WarnLevel
	case "error":
		level = zapcore.ErrorLevel
	case "fatal":
		level = zapcore.FatalLevel
	default:
		level = zapcore.InfoLevel
	}

	// Configure encoder
	encoderConfig := zapcore.EncoderConfig{
		TimeKey:        "time",
		LevelKey:       "level",
		NameKey:        "logger",
		CallerKey:      "caller",
		MessageKey:     "msg",
		StacktraceKey:  "stacktrace",
		LineEnding:     zapcore.DefaultLineEnding,
		EncodeLevel:    zapcore.LowercaseLevelEncoder,
		EncodeTime:     zapcore.TimeEncoder(func(t time.Time, enc zapcore.PrimitiveArrayEncoder) { enc.AppendString(t.Format(config.TimeFormat)) }),
		EncodeDuration: zapcore.SecondsDurationEncoder,
		EncodeCaller:   zapcore.ShortCallerEncoder,
	}

	// Create encoder based on format
	var encoder zapcore.Encoder
	if config.Format == "json" {
		encoder = zapcore.NewJSONEncoder(encoderConfig)
	} else {
		encoder = zapcore.NewConsoleEncoder(encoderConfig)
	}

	// Set output
	output := config.Output
	if output == nil {
		output = os.Stdout
	}
	writeSyncer := zapcore.AddSync(output)

	// Create core and logger
	core := zapcore.NewCore(encoder, writeSyncer, level)
	zapLog := zap.New(core, zap.AddCaller(), zap.AddStacktrace(zapcore.ErrorLevel))

	return &ZapLogger{logger: zapLog}, nil
}

// Debug logs a debug message
func (l *ZapLogger) Debug(msg string, fields ...Field) {
	l.logger.Debug(msg, fieldsToZapFields(fields)...)
}

// Info logs an info message
func (l *ZapLogger) Info(msg string, fields ...Field) {
	l.logger.Info(msg, fieldsToZapFields(fields)...)
}

// Warn logs a warning message
func (l *ZapLogger) Warn(msg string, fields ...Field) {
	l.logger.Warn(msg, fieldsToZapFields(fields)...)
}

// Error logs an error message
func (l *ZapLogger) Error(msg string, fields ...Field) {
	l.logger.Error(msg, fieldsToZapFields(fields)...)
}

// Fatal logs a fatal message and exits
func (l *ZapLogger) Fatal(msg string, fields ...Field) {
	l.logger.Fatal(msg, fieldsToZapFields(fields)...)
}

// With returns a logger with the fields added to it
func (l *ZapLogger) With(fields ...Field) Logger {
	return &ZapLogger{logger: l.logger.With(fieldsToZapFields(fields)...)}
}

// WithContext returns a logger with the context
func (l *ZapLogger) WithContext(ctx context.Context) Logger {
	// Context not used in this implementation
	return l
}

// Helper functions for creating fields
func fieldsToZapFields(fields []Field) []zap.Field {
	zapFields := make([]zap.Field, 0, len(fields))
	for _, field := range fields {
		zapFields = append(zapFields, zap.Any(field.Key, field.Value))
	}
	return zapFields
}

// Field helpers
func String(key string, value string) Field   { return Field{Key: key, Value: value} }
func Int(key string, value int) Field         { return Field{Key: key, Value: value} }
func Int64(key string, value int64) Field     { return Field{Key: key, Value: value} }
func Float64(key string, value float64) Field { return Field{Key: key, Value: value} }
func Bool(key string, value bool) Field       { return Field{Key: key, Value: value} }
func Error(err error) Field {
	if err == nil {
		return Field{Key: "error", Value: nil}
	}
	return Field{Key: "error", Value: err.Error()}
}
func Any(key string, value interface{}) Field        { return Field{Key: key, Value: value} }
func Duration(key string, value time.Duration) Field { return Field{Key: key, Value: value} }
